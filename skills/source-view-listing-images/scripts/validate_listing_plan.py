#!/usr/bin/env python3
"""Validate a source-driven multilingual Listing plan before generation."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


VISUAL_ROLES = {
    "exact_layout_and_source_view_reference",
    "exact_product_view_reference",
    "real_person_source_lock",
}
ROLE_ALIASES = {
    "exact_product_surface_melo_city_print_reference": "exact_product_surface_print_reference",
    "inner_x_topology_reference_only": "inner_topology_reference_only",
    "exact_main_fabric_visual_reference": "exact_material_macro_reference",
    "exact_inner_gusset_visual_reference": "exact_material_macro_reference",
}
PRODUCT_ROLES = VISUAL_ROLES | {
    "exact_large_production_outer_product_colour_logo_reference",
    "exact_product_surface_print_reference",
    "exact_material_macro_reference",
}
NON_PRIMARY_ROLES = {
    "composition_data_reference_only",
    "size_data_reference_only",
    "selected_colour_mapping_reference",
    "white_background_fidelity_anchor",
    "inner_topology_reference_only",
    "style_reference_only",
    "virtual_model_identity_reference_only",
}
DETAIL_SOURCE_FAMILIES = {"source_detail", "source_main", "product_original", "product_macro", "verified_data"}
SENSITIVE_CLAIMS = re.compile(
    r"antibacter|抗菌|抑菌|hpv|香氛|塑形|瘦|提臀|support|支撑|治疗|治愈|认证|certif",
    re.I,
)
STATUS_ORDER = {"pass": 0, "pending": 1, "missing evidence": 2, "fail": 3}


def add(issues: list[dict[str, str]], status: str, code: str, message: str, task: str = "") -> None:
    issues.append({"status": status, "code": code, "task_id": task, "message": message})


def canonical_role(role: str) -> str:
    return ROLE_ALIASES.get(role, role)


def colour_labels(values: Any) -> set[str]:
    """Accept legacy colour mappings without silently losing their labels.

    Older plans sometimes store the selected colour as an object with Chinese,
    English, and Malay labels.  The validator only needs a comparison set, so
    collect every non-empty textual label while preserving the original plan.
    """
    labels: set[str] = set()
    for value in values or []:
        if isinstance(value, str):
            text = value.strip()
            if text:
                labels.add(text)
            continue
        if not isinstance(value, dict):
            continue
        for key in (
            "name",
            "label",
            "ms",
            "en",
            "zh",
            "crossborder_colour",
            "local_store_colour",
            "spreadsheet_colour",
        ):
            text = str(value.get(key, "")).strip()
            if text:
                labels.add(text)
    return labels


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Listing evidence bindings and set design.")
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--skip-path-check", action="store_true")
    args = parser.parse_args()

    plan = json.loads(args.plan.expanduser().read_text(encoding="utf-8"))
    issues: list[dict[str, str]] = []
    tasks = plan.get("tasks") or []
    policy = plan.get("set_policy") or {}
    shentai = policy.get("profile") == "shentai-ms"
    expected_main = int(policy.get("expected_main", 8 if shentai else 9))
    min_detail = int(policy.get("min_detail", 9 if shentai else 4))
    max_detail = int(policy.get("max_detail", 9 if shentai else 6))
    max_flat = int(policy.get("max_flat_lay_main", 3))
    selected_colours = colour_labels(plan.get("selected_colours"))

    if not plan.get("product"):
        add(issues, "fail", "missing_product", "Plan must include product.")
    if not plan.get("source_language") or not plan.get("target_language"):
        add(issues, "pending", "missing_language", "Record source_language and target_language.")
    if not selected_colours:
        add(issues, "missing evidence", "missing_selected_colours", "No selected SKU colours are recorded.")
    if not tasks:
        add(issues, "fail", "missing_tasks", "Plan has no tasks.")

    ids = [str(task.get("id", "")) for task in tasks]
    for duplicate, count in Counter(ids).items():
        if duplicate and count > 1:
            add(issues, "fail", "duplicate_task_id", f"Task id appears {count} times: {duplicate}", duplicate)

    groups = Counter(str(task.get("group", "")) for task in tasks)
    if groups["main"] != expected_main:
        add(issues, "fail", "main_count", f"Expected {expected_main} mains, found {groups['main']}.")
    if not min_detail <= groups["detail"] <= max_detail:
        add(issues, "fail", "detail_count", f"Expected {min_detail}-{max_detail} details, found {groups['detail']}.")

    flat_main = sum(bool(task.get("flat_lay")) for task in tasks if task.get("group") == "main")
    if flat_main > max_flat:
        add(issues, "fail", "flat_lay_dominance", f"Flat-lay mains {flat_main} exceed limit {max_flat}.")

    decision_questions: list[str] = []
    visual_roles: list[str] = []
    primary_paths: list[str] = []

    for task in tasks:
        task_id = str(task.get("id", ""))
        group = str(task.get("group", ""))
        ratio = str(task.get("ratio", ""))
        expected_ratio = "1:1" if group == "main" else "9:16" if group == "detail" else ""
        if not task_id or group not in {"main", "detail"}:
            add(issues, "fail", "task_identity", "Each task needs id and group main/detail.", task_id)
        if expected_ratio and ratio != expected_ratio:
            add(issues, "fail", "ratio", f"{group} requires {expected_ratio}, found {ratio or 'missing'}.", task_id)

        decision = str(task.get("decision_question", "")).strip()
        selling_point = str(task.get("selling_point", "")).strip()
        visual_role = str(task.get("visual_role", "")).strip()
        if not decision:
            add(issues, "fail", "missing_decision_question", "Bind one purchase-decision question.", task_id)
        else:
            decision_questions.append(decision.casefold())
        if not selling_point:
            add(issues, "fail", "missing_selling_point", "Bind one selling point.", task_id)
        if not visual_role:
            add(issues, "fail", "missing_visual_role", "Bind a distinct visual role.", task_id)
        else:
            visual_roles.append(visual_role)

        evidence_status = str(task.get("evidence_status", "pending"))
        if evidence_status != "pass":
            add(issues, evidence_status if evidence_status in STATUS_ORDER else "pending", "evidence_not_pass", f"Evidence status is {evidence_status}.", task_id)

        copy = task.get("target_copy") or {}
        if not str(copy.get("headline", "")).strip():
            add(issues, "fail", "missing_target_copy", "Target-language headline is required.", task_id)

        colours = set(task.get("colours") or [])
        unknown_colours = colours - selected_colours
        if unknown_colours:
            add(issues, "fail", "unselected_colour", f"Colours not selected in spreadsheet: {sorted(unknown_colours)}.", task_id)

        references = task.get("references") or []
        if not references:
            add(issues, "missing evidence", "missing_references", "No source references are bound.", task_id)
            continue
        roles = [canonical_role(str(reference.get("role", ""))) for reference in references]
        primary_role = roles[0]
        primary_path = str(references[0].get("path", ""))
        if primary_path:
            primary_paths.append(primary_path)
        if primary_role in NON_PRIMARY_ROLES:
            add(issues, "fail", "invalid_primary_role", f"Primary reference role cannot be {primary_role}.", task_id)
        if not any(role in VISUAL_ROLES for role in roles):
            add(issues, "missing evidence", "missing_source_view", "No exact layout/product/person source-view reference.", task_id)
        if not any(role in PRODUCT_ROLES for role in roles):
            add(issues, "missing evidence", "missing_product_truth", "No reference controls product truth.", task_id)
        if all(role in {"white_background_fidelity_anchor", "style_reference_only"} for role in roles):
            add(issues, "fail", "anchor_only", "White-background/style references cannot be the entire evidence set.", task_id)
        for reference in references:
            path_text = str(reference.get("path", ""))
            if not path_text:
                add(issues, "fail", "reference_path", "Reference path is missing.", task_id)
            elif not args.skip_path_check and not Path(path_text).expanduser().exists():
                add(issues, "missing evidence", "reference_missing", f"Reference file does not exist: {path_text}", task_id)
            if not reference.get("role"):
                add(issues, "fail", "reference_role", f"Reference role is missing: {path_text}", task_id)

        if shentai and group == "detail":
            families = {str(ref.get("source_family", "")) for ref in references}
            if "generated_main" in families:
                add(issues, "fail", "detail_uses_generated_main", "Use original references for the detail page, not a generated main.", task_id)
            if not families & DETAIL_SOURCE_FAMILIES:
                add(issues, "missing evidence", "detail_original_source", "Bind an original product, source view, or verified data reference.", task_id)

        identities = [ref for ref, role in zip(references, roles) if role == "virtual_model_identity_reference_only"]
        if task.get("contains_virtual_model") or identities:
            expected_master = str(policy.get("virtual_model_master", "")).strip()
            if not expected_master or len(identities) != 1:
                add(issues, "missing evidence", "virtual_identity", "A virtual model task requires one approved identity master reference.", task_id)
            else:
                actual_master = str(identities[0].get("path", ""))
                if Path(actual_master).expanduser().resolve() != Path(expected_master).expanduser().resolve():
                    add(issues, "fail", "virtual_identity_mismatch", "Virtual model reference differs from the approved master.", task_id)

        if task.get("contains_real_person") or task.get("contains_real_hand"):
            if not task.get("preserve_body"):
                add(issues, "fail", "body_not_locked", "Human/hand task must set preserve_body=true.", task_id)
            channel = str(task.get("channel", "")).casefold()
            if not any(token in channel for token in ("source-lock", "source_lock", "gemini", "banana", "edit")):
                add(issues, "pending", "human_channel", "Human/hand task lacks an explicit source-lock editing channel.", task_id)
            if "real_person_source_lock" not in roles and "exact_layout_and_source_view_reference" not in roles:
                add(issues, "missing evidence", "human_source", "Human/hand task lacks a real source lock.", task_id)

        claim_status = str(task.get("claim_status", ""))
        claim_text = " ".join([selling_point, str(copy.get("headline", "")), str(copy.get("support", ""))])
        if SENSITIVE_CLAIMS.search(claim_text):
            if claim_status not in {"claim_evidence_pending", "verified"}:
                add(issues, "missing evidence", "claim_status", "Sensitive claim needs claim_evidence_pending or verified.", task_id)
            if claim_status == "verified" and not task.get("claim_evidence"):
                add(issues, "missing evidence", "claim_evidence", "Verified claim has no evidence record.", task_id)
        elif not claim_status:
            add(issues, "pending", "claim_status_missing", "Record claim_status even when no sensitive claim is used.", task_id)

    for question, count in Counter(decision_questions).items():
        if count > 1:
            add(issues, "fail", "duplicate_decision_question", f"Decision question repeats {count} times: {question}")
    for role, count in Counter(visual_roles).items():
        if count > 2:
            add(issues, "pending", "repeated_visual_role", f"Visual role repeats {count} times: {role}")
    for path, count in Counter(primary_paths).items():
        if count > 2:
            add(issues, "pending", "reused_primary_source", f"Primary source reused {count} times: {path}")

    overall = "pass"
    if issues:
        overall = max((issue["status"] for issue in issues), key=lambda status: STATUS_ORDER.get(status, 1))
    result: dict[str, Any] = {
        "product": plan.get("product"),
        "status": overall,
        "counts": {
            "tasks": len(tasks),
            "main": groups["main"],
            "detail": groups["detail"],
            "flat_lay_main": flat_main,
            "issues": len(issues),
        },
        "issues": issues,
    }
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    print(output, end="")
    if args.output:
        args.output.expanduser().parent.mkdir(parents=True, exist_ok=True)
        args.output.expanduser().write_text(output, encoding="utf-8")
    return 0 if overall == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
