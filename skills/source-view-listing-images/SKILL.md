---
name: source-view-listing-images
description: "Build or repair multilingual ecommerce Listing image sets from product selling points, Chinese or other source-language main/detail images, exact SKU references, and real or virtual model references. Create and review main images, mobile detail pages, SKU white-background photos, and image-by-image PDFs. Includes the SHENTAI Malay workflow (商品卖点、中文参考图、模特图、马来语主图、详情图、SKU 白底图、定稿归档). Excludes standalone translation, copywriting, and generic photo retouching."
---

# Source-View Multilingual Listing Images

## Workflow

1. Read project rules and the selected brief. For 身态马来语商品图 use [SHENTAI workflow](references/shentai-malay-listing.md). Other requests use the [general SOP](references/workflow.md).
2. Inventory and deduplicate without deleting. Separate product truth, visual demonstration, real/virtual model identity, data, and style references. Exact same-SKU originals govern color and construction. Approved data governs sizes and claims. Use [evidence schema](references/evidence-schema.md) and prepare `SOURCE_COLOR_ANCHOR_GATE.json` per selected color.
3. Map each purchase question to one selling point, source view, target copy and image slot. Validate `LISTING_PLAN.json` with `scripts/validate_listing_plan.py --plan <file>`. Apply requested counts or profile defaults. Mark unsupported colors, claims or features as missing evidence. Finish unaffected work while resolving gaps.
4. Use the requested and permitted generator. Real-model/hand edits lock identity, pose and crop to original pixels. Virtual-model tasks bind one approved identity master and exact product evidence. Design original detail pages from source materials. Use local processing for approved branding, export and review previews, with final edits following the project rules.
5. Verify actual pixels and rendered text. Use [review rubric](references/review-rubric.md), `scripts/local_visual_review.py`, and `scripts/audit_listing_set.py`. Review the set for distinct visual roles. Repair failed slots and recheck the set. See [failure modes](references/failure-modes.md).
6. Deliver the reviewed candidates, image-by-image PDF and relevant previews. Archive the approved version by style and category with source hashes. Platform publishing and formal asset replacement require separate scope, snapshots and readback.

## Contract

Owner: vanch / Codex. Review after a failed batch, standard change or generator change. Local Codex workflow. Product sources and model references are user data. Send them only to an authorized generation route. Do not change vendor factual claims merely because they appear in reference artwork. A generated output or OCR pass is not release approval.

Keep source index, selling-point mapping, plan, request logs, reviewed candidates, PDF and export hashes. Preserve the previous version for rollback. Routing cases are in `evals/trigger_cases.json` and local replay evidence in `reports/output_quality_scorecard.md`.
