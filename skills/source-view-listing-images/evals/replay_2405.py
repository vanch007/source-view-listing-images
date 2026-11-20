#!/usr/bin/env python3
"""Read-only replay against the project's 2405 sources and approved archive."""

import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

import fitz
from PIL import Image

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--project-root", required=True, type=Path)
root = parser.parse_args().project_root.resolve(strict=True)
skill = Path(__file__).resolve().parents[1]
validator = skill / "scripts/validate_listing_plan.py"

original = root / "产品/女士内衣内裤/2405"
batch = root / "Listing图片制作与审核"
master = batch / "brand_virtual_models_my_20261117/master_sheets/model_b1_chic_bob_4view_generated_1.jpg"
product = original / "颜色/07.jpg"
main_view = original / "2405 (1).jpg"
detail_view = original / "详情/2405详情页_08.jpg"
archive = root / "马来语商品图片定稿"

def task(group, view, family, question, point, headline):
    return {
        "id": f"{group}_01",
        "group": group,
        "ratio": "1:1" if group == "main" else "9:16",
        "decision_question": question,
        "selling_point": point,
        "visual_role": f"{group}_product_view",
        "colours": ["Hitam"],
        "target_copy": {"headline": headline},
        "claim_status": "pass",
        "evidence_status": "pass",
        "references": [
            {"role": "exact_layout_and_source_view_reference", "source_family": family, "path": str(view)},
            {"role": "exact_product_view_reference", "source_family": "product_original", "path": str(product)},
        ],
    }

main = task("main", main_view, "source_main", "Bagaimana rupa ketika dipakai?", "Renda leher V", "Kamisol renda leher V")
main["contains_virtual_model"] = True
main["references"].append({"role": "virtual_model_identity_reference_only", "path": str(master)})
detail = task("detail", detail_view, "source_detail", "Bagaimana potongan belakang?", "Renda silang", "Renda motif orkid")
plan = {
    "product": "2405",
    "source_language": "zh-CN",
    "target_language": "ms-MY",
    "selected_colours": ["Hitam"],
    "set_policy": {
        "profile": "shentai-ms", "expected_main": 1, "min_detail": 1, "max_detail": 1,
        "virtual_model_master": str(master),
    },
    "tasks": [main, detail],
}

def issue_codes(document):
    with TemporaryDirectory() as tmp:
        candidate = Path(tmp) / "plan.json"
        candidate.write_text(json.dumps(document))
        result = subprocess.run(
            [sys.executable, str(validator), "--plan", str(candidate)], capture_output=True, text=True,
        )
        assert result.returncode in (0, 1), result.stderr
        return {issue["code"] for issue in json.loads(result.stdout)["issues"]}

assert not issue_codes(plan)
wrong_model = deepcopy(plan)
wrong_model["tasks"][0]["references"][-1]["path"] = str(main_view)
assert "virtual_identity_mismatch" in issue_codes(wrong_model)
missing_identity = deepcopy(plan)
missing_identity["tasks"][0]["references"].pop()
assert "virtual_identity" in issue_codes(missing_identity)
reused_main = deepcopy(plan)
reused_main["tasks"][1]["references"][0].update(
    path=str(archive / "2405/主图/01_hero.jpg"), source_family="generated_main",
)
assert "detail_uses_generated_main" in issue_codes(reused_main)
missing_detail = deepcopy(plan)
for reference in missing_detail["tasks"][1]["references"]:
    reference.pop("source_family", None)
assert "detail_original_source" in issue_codes(missing_detail)
legacy = deepcopy(plan)
legacy["set_policy"].pop("profile")
legacy["tasks"][0].pop("contains_virtual_model")
legacy["tasks"][0]["references"].pop()
assert not issue_codes(legacy)

rows = json.loads((archive / "归档来源.json").read_text())["styles"]["2405"]
groups = ("主图", "详情图", "SKU 白底图")
assert Counter(row["category"] for row in rows) == dict(zip(groups, (8, 9, 2)))
ordered = sorted(rows, key=lambda row: (groups.index(row["category"]), row["name"]))
with fitz.open(archive / "2405/2405_商品图片说明.pdf") as pdf:
    assert len(pdf) == 21
    for index, row in enumerate(ordered, 2):
        path = archive / "2405" / row["category"] / row["name"]
        assert sha256(path.read_bytes()).hexdigest() == row["sha256"]
        with Image.open(path) as image:
            image.load()
            assert list(image.size) == row["dimensions"]
        reference, = pdf[index].get_images()
        assert sha256(pdf.extract_image(reference[0])["image"]).hexdigest() == row["sha256"]

print("PASS: 6 plan cases, 19 archived images (8/9/2), 21 PDF pages and 19 matching embedded images")
