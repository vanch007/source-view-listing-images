#!/usr/bin/env python3
"""Audit Listing counts, ratios, source locks, and perceptual duplicates."""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path
from typing import Any

import cv2
import numpy as np


def read_gray(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Cannot read image: {path}")
    return image


def sift_ransac(source: Path, candidate: Path) -> tuple[int, int]:
    source_image = read_gray(source)
    candidate_image = read_gray(candidate)
    sift = cv2.SIFT_create(nfeatures=5000)
    source_points, source_descriptors = sift.detectAndCompute(source_image, None)
    candidate_points, candidate_descriptors = sift.detectAndCompute(candidate_image, None)
    if source_descriptors is None or candidate_descriptors is None:
        return 0, 0
    matches = cv2.BFMatcher(cv2.NORM_L2).knnMatch(source_descriptors, candidate_descriptors, k=2)
    good = [first for first, second in matches if first.distance < 0.75 * second.distance]
    if len(good) < 4:
        return len(good), 0
    source_xy = np.float32([source_points[item.queryIdx].pt for item in good])
    candidate_xy = np.float32([candidate_points[item.trainIdx].pt for item in good])
    _, mask = cv2.findHomography(source_xy, candidate_xy, cv2.RANSAC, 5.0)
    return len(good), int(mask.sum()) if mask is not None else 0


def phash(path: Path) -> int:
    image = read_gray(path)
    resized = cv2.resize(image, (32, 32), interpolation=cv2.INTER_AREA)
    values = cv2.dct(np.float32(resized))[:8, :8].flatten()
    median = float(np.median(values[1:]))
    result = 0
    for bit in values > median:
        result = (result << 1) | int(bit)
    return result


def image_record(path: Path, main_tolerance: float, detail_tolerance: float) -> dict[str, Any]:
    image = read_gray(path)
    height, width = image.shape[:2]
    actual = width / height
    if path.stem.startswith("main_"):
        expected = 1.0
        tolerance = main_tolerance
        group = "main"
    elif path.stem.startswith("detail_"):
        expected = 9 / 16
        tolerance = detail_tolerance
        group = "detail"
    else:
        return {"id": path.stem, "path": str(path), "status": "fail", "reason": "unknown filename group"}
    relative_error = abs(actual - expected) / expected
    return {
        "id": path.stem,
        "path": str(path),
        "group": group,
        "width": width,
        "height": height,
        "actual_ratio": round(actual, 6),
        "expected_ratio": round(expected, 6),
        "relative_error": round(relative_error, 6),
        "status": "pass" if relative_error <= tolerance else "fail",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a reviewed Listing image directory.")
    parser.add_argument("--image-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pairs-json", type=Path)
    parser.add_argument("--expected-main", type=int, default=9)
    parser.add_argument("--min-detail", type=int, default=4)
    parser.add_argument("--max-detail", type=int, default=6)
    parser.add_argument("--main-ratio-tolerance", type=float, default=0.03)
    parser.add_argument("--detail-ratio-tolerance", type=float, default=0.18)
    parser.add_argument("--duplicate-threshold", type=int, default=8)
    parser.add_argument("--min-good-matches", type=int, default=15)
    parser.add_argument("--min-ransac-inliers", type=int, default=6)
    args = parser.parse_args()

    image_dir = args.image_dir.expanduser().resolve()
    images = sorted(
        path
        for path in image_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )
    records = [image_record(path, args.main_ratio_tolerance, args.detail_ratio_tolerance) for path in images]
    main_count = sum(record.get("group") == "main" for record in records)
    detail_count = sum(record.get("group") == "detail" for record in records)
    count_status = "pass" if main_count == args.expected_main and args.min_detail <= detail_count <= args.max_detail else "fail"
    ratio_status = "pass" if records and all(record["status"] == "pass" for record in records) else "fail"

    hashes = {path.stem: phash(path) for path in images}
    distances = [
        {"a": left, "b": right, "distance": (hashes[left] ^ hashes[right]).bit_count()}
        for left, right in combinations(hashes, 2)
    ]
    distances.sort(key=lambda item: (item["distance"], item["a"], item["b"]))
    duplicates = [item for item in distances if item["distance"] <= args.duplicate_threshold]
    duplicate_status = "pass" if not duplicates else "fail"

    source_locks = []
    if args.pairs_json:
        pairs = json.loads(args.pairs_json.expanduser().read_text(encoding="utf-8"))
        for pair in pairs:
            task_id = str(pair.get("id") or "")
            source = Path(pair.get("source") or pair.get("source_path")).expanduser().resolve()
            candidate_text = pair.get("candidate") or pair.get("candidate_path")
            candidate = Path(candidate_text).expanduser().resolve() if candidate_text else image_dir / f"{task_id}.jpg"
            if not candidate.exists() and not candidate_text:
                candidate = image_dir / f"{task_id}.png"
            good, inliers = sift_ransac(source, candidate)
            status = "pass" if good >= args.min_good_matches and inliers >= args.min_ransac_inliers else "fail"
            source_locks.append(
                {
                    "id": task_id,
                    "source": str(source),
                    "candidate": str(candidate),
                    "good_matches": good,
                    "ransac_inliers": inliers,
                    "minimum_good_matches": args.min_good_matches,
                    "minimum_ransac_inliers": args.min_ransac_inliers,
                    "status": status,
                }
            )
    source_lock_status = "pass" if not source_locks or all(item["status"] == "pass" for item in source_locks) else "fail"

    statuses = [count_status, ratio_status, duplicate_status, source_lock_status]
    result = {
        "status": "pass" if all(status == "pass" for status in statuses) else "fail",
        "image_dir": str(image_dir),
        "counts": {
            "main": main_count,
            "detail": detail_count,
            "expected_main": args.expected_main,
            "min_detail": args.min_detail,
            "max_detail": args.max_detail,
            "status": count_status,
        },
        "ratios": {"status": ratio_status, "images": records},
        "source_locks": {"status": source_lock_status, "pairs": source_locks},
        "phash": {
            "status": duplicate_status,
            "threshold": args.duplicate_threshold,
            "duplicate_count": len(duplicates),
            "minimum_distance": distances[0]["distance"] if distances else None,
            "duplicates": duplicates,
            "closest_pairs": distances[:10],
        },
    }
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    args.output.expanduser().parent.mkdir(parents=True, exist_ok=True)
    args.output.expanduser().write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
