#!/usr/bin/env python3
"""Run role-aware multi-reference Listing review with a local VLM."""

from __future__ import annotations

import argparse
import base64
import io
import json
import re
import urllib.request
from pathlib import Path
from typing import Any

from PIL import Image


DEFAULT_MODEL = "Qwen3.6-35B-A3B-Qwable-Holo3-Qwopus-oQ6-mtp"
IMAGE_SUFFIXES = {".avif", ".bmp", ".gif", ".jpeg", ".jpg", ".png", ".webp"}


def is_visual_reference(reference: dict[str, Any]) -> bool:
    """Keep data-only evidence in the audit without sending it to the VLM as an image."""
    role = str(reference.get("role", ""))
    path = Path(str(reference.get("path", ""))).expanduser()
    return "data_reference_only" not in role and path.suffix.lower() in IMAGE_SUFFIXES


def image_data_url(path: Path, max_side: int) -> str:
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        rgb.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        rgb.save(buffer, "JPEG", quality=88, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode()


def parse_json(text: str) -> dict[str, Any]:
    cleaned = re.sub(r"^```(?:json)?|```$", "", (text or "").strip()).strip()
    try:
        value = json.loads(cleaned)
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.S)
        if not match:
            return {}
        try:
            value = json.loads(match.group(0))
            return value if isinstance(value, dict) else {}
        except json.JSONDecodeError:
            return {}


def review_prompt(task: dict[str, Any], target_language: str) -> str:
    roles = "\n".join(
        f"- Reference {index + 1}: {reference.get('role', 'unknown')}"
        + (" (data-only provenance; no image supplied to the reviewer)" if not is_visual_reference(reference) else "")
        for index, reference in enumerate(task.get("references") or [])
    )
    return f"""
You will receive all controlling references in the listed order, then the final candidate image.
Review the candidate against each reference only within that reference's declared role.

Authority order: selected SKU/data and exact physical product > source marketing/detail view > data-only reference > style > prompt/candidate.

Role rules:
- exact_layout_and_source_view_reference: preserve composition, crop, camera view, and visible selling-point demonstration; translated text/layout may change.
- exact_product_view_reference: preserve the visible product exactly.
- exact_large_production_outer_product_colour_logo_reference: preserve bulk silhouette, selected color, outer material, trim, and physical print.
- exact_product_surface_print_reference: preserve exact spelling, layer count, placement, contrast, and orientation of the physical print/logo.
- real_person_source_lock: preserve face, body, pose, hands, crop, anatomy, and garment boundaries; generated body extension fails.
- inner_topology_reference_only: controls internal layer position only; it must not redefine outer appearance or become an exaggerated external feature.
- exact_material_macro_reference: controls visible texture/finish only.
- composition_data_reference_only and size_data_reference_only: control exact rendered values only, not product appearance.
- white_background_fidelity_anchor: verifies silhouette/color only; it must not erase the selling-point composition.
- style_reference_only: controls graphics only and never product/data/claims.
- Legacy aliases are equivalent: exact_product_surface_melo_city_print_reference -> exact_product_surface_print_reference; inner_x_topology_reference_only -> inner_topology_reference_only; exact_main_fabric_visual_reference/exact_inner_gusset_visual_reference -> exact_material_macro_reference.

Also review rendered text: {target_language} should be dominant; exact colors, sizes, percentages, material names, and physical brand spelling must be correct. Separate text issues from product issues. Flag absolute, therapeutic, guaranteed, or unsupported result claims.

Task: {task.get('id', '')}
Decision question: {task.get('decision_question', '')}
Selling point: {task.get('selling_point', '')}
Visual role: {task.get('visual_role', '')}
Selected colours: {', '.join(task.get('colours') or [])}
Expected headline: {(task.get('target_copy') or {}).get('headline', task.get('title_ms', ''))}
References:
{roles}

Return valid JSON only. Do not use unescaped ASCII double quotes inside any string value; use Chinese quotation marks or omit the quoted phrase instead.

Return JSON only:
{{
  "status": "pass|fail|pending|missing evidence",
  "summary_zh": "",
  "product_issues": [],
  "body_issues": [],
  "colour_issues": [],
  "text_issues": [],
  "claim_issues": [],
  "recommendation_zh": ""
}}
""".strip()


def post(base_url: str, payload: dict[str, Any], timeout: int) -> str:
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    return str((data.get("choices") or [{}])[0].get("message", {}).get("content", ""))


def review_task(
    task: dict[str, Any], candidate_dir: Path, extension: str, model: str,
    base_url: str, max_side: int, timeout: int, target_language: str,
) -> dict[str, Any]:
    task_id = str(task.get("id", ""))
    references = task.get("references") or []
    visual_references = [reference for reference in references if is_visual_reference(reference)]
    data_only_references = [reference for reference in references if not is_visual_reference(reference)]
    candidate = candidate_dir / f"{task_id}{extension}"
    missing = [str(reference.get("path", "")) for reference in references if not Path(str(reference.get("path", ""))).expanduser().exists()]
    if not candidate.exists():
        missing.append(str(candidate))
    if not visual_references or missing:
        return {
            "id": task_id,
            "status": "missing evidence",
            "summary_zh": "缺少视觉参考图或候选图",
            "missing_paths": missing,
            "model": model,
            "candidate_path": str(candidate),
        }

    content: list[dict[str, Any]] = [{"type": "text", "text": review_prompt(task, target_language)}]
    for reference in visual_references:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": image_data_url(Path(reference["path"]).expanduser(), max_side)},
            }
        )
    content.append({"type": "image_url", "image_url": {"url": image_data_url(candidate, max_side)}})
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0,
        "max_tokens": 900,
    }
    try:
        raw = post(base_url, payload, timeout)
        parsed = parse_json(raw)
        if not parsed:
            parsed = {"status": "pending", "summary_zh": "模型输出无法解析", "raw_text": raw[:2000]}
    except Exception as error:
        parsed = {"status": "pending", "summary_zh": f"{type(error).__name__}: {error}"}
    parsed.update(
        {
            "id": task_id,
            "model": model,
            "candidate_path": str(candidate),
            "references": references,
            "visual_references": visual_references,
            "data_only_references": data_only_references,
        }
    )
    return parsed


def write_markdown(path: Path, product: str, model: str, results: list[dict[str, Any]]) -> None:
    counts = {status: sum(item.get("status") == status for item in results) for status in ("pass", "fail", "pending", "missing evidence")}
    lines = [
        f"# {product} 本地多参考 Listing 审核", "", f"- model: `{model}`",
        f"- pass: {counts['pass']}", f"- fail: {counts['fail']}",
        f"- pending: {counts['pending']}", f"- missing evidence: {counts['missing evidence']}", "",
    ]
    for item in results:
        lines.extend(
            [
                f"## {item.get('id')} - `{item.get('status')}`", "",
                f"- 结论：{item.get('summary_zh', '')}",
                f"- 商品问题：{'；'.join(item.get('product_issues') or []) or '无'}",
                f"- 人体问题：{'；'.join(item.get('body_issues') or []) or '无'}",
                f"- 颜色问题：{'；'.join(item.get('colour_issues') or []) or '无'}",
                f"- 文字问题：{'；'.join(item.get('text_issues') or []) or '无'}",
                f"- 声明问题：{'；'.join(item.get('claim_issues') or []) or '无'}",
                f"- 建议：{item.get('recommendation_zh', '')}", "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Review a Listing plan against multi-role references.")
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path)
    parser.add_argument("--task", action="append", default=[])
    parser.add_argument("--candidate-extension", default=".jpg")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--image-max-side", type=int, default=1000)
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    plan = json.loads(args.plan.expanduser().read_text(encoding="utf-8"))
    selected = set(args.task)
    tasks = [task for task in plan.get("tasks", []) if not selected or task.get("id") in selected]
    results = []
    for task in tasks:
        result = review_task(
            task, args.candidate_dir.expanduser().resolve(), args.candidate_extension,
            args.model, args.base_url, args.image_max_side, args.timeout,
            str(plan.get("target_language", "target language")),
        )
        results.append(result)
        print(f"{result.get('id')}: {result.get('status')}", flush=True)
    args.output_json.expanduser().parent.mkdir(parents=True, exist_ok=True)
    args.output_json.expanduser().write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.output_markdown:
        write_markdown(args.output_markdown.expanduser(), str(plan.get("product", args.plan.stem)), args.model, results)
    return 0 if results and all(result.get("status") == "pass" for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
