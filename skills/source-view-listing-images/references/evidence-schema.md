# Listing Evidence And Plan Schema

## Contents

1. Status vocabulary
2. Reference roles
3. Source index record
4. Evidence matrix row
5. Listing plan JSON
6. Generation and review records

## 1. Status Vocabulary

- `pass`: evidence and required checks are closed.
- `fail`: evidence proves a requirement is violated.
- `pending`: evidence exists but review is incomplete or ambiguous.
- `missing evidence`: required evidence does not exist or cannot establish the fact.
- `rejected`: historical candidate/version that must not be published.
- `claim_evidence_pending`: copy may be planned conservatively, but the performance claim is not verified.

Do not use `complete`, `ready`, or `final` as evidence statuses.

## 2. Reference Roles

Use stable role names so prompts, reviews, PDFs, and audits agree.

| Role | Controls | Must not control |
|---|---|---|
| `exact_layout_and_source_view_reference` | composition, crop, camera view, visible demonstration, source visual language | unseen product facts |
| `exact_product_view_reference` | exact visible product view and construction | unrelated layout or data |
| `exact_large_production_outer_product_colour_logo_reference` | bulk silhouette, selected color, outer material, trim, physical print | layout, inner topology |
| `exact_product_surface_print_reference` | spelling, layer count, position, contrast, orientation of physical print/logo | whole product silhouette |
| `real_person_source_lock` | face, body, pose, hands, crop, garment boundaries | generated body extension |
| `virtual_model_identity_reference_only` | selected virtual model’s face, hair and body proportions | product truth, layout, or reference people from other artwork |
| `inner_topology_reference_only` | internal layer location/topology | outer color, surface, background, visibility strength |
| `exact_material_macro_reference` | texture, knit/lace pattern, edge/finish | whole product view |
| `composition_data_reference_only` | exact percentages and component labels | product appearance |
| `size_data_reference_only` | exact size values and units | product appearance |
| `selected_colour_mapping_reference` | supplier/source file to selected color-name mapping | product structure |
| `white_background_fidelity_anchor` | silhouette/color verification | creative selling-point composition unless explicitly justified |
| `style_reference_only` | typography, spacing, mood, graphic system | product, data, claims, colors |

A reference can be reused across slots, but the primary source view should not be reused repeatedly without a distinct decision role and visual treatment.

Legacy project artifacts may use these aliases; normalize them when creating new plans:

- `exact_product_surface_melo_city_print_reference` -> `exact_product_surface_print_reference`
- `inner_x_topology_reference_only` -> `inner_topology_reference_only`
- `exact_main_fabric_visual_reference` -> `exact_material_macro_reference`
- `exact_inner_gusset_visual_reference` -> `exact_material_macro_reference`

## 3. Source Index Record

```json
{
  "source_id": "src_main_004",
  "path": "/absolute/path/4.jpg",
  "family": "source_marketing_main",
  "sha256": "...",
  "phash": "...",
  "dimensions": [800, 800],
  "aspect": "1:1",
  "duplicate_of": null,
  "language": "zh-CN",
  "source_text": ["..."],
  "contains_real_person": false,
  "contains_real_hand": false,
  "product_view": "five-colour still life",
  "visible_facts": ["floral lace", "high waist"],
  "selling_point_visuals": ["color choice"],
  "allowed_roles": ["exact_layout_and_source_view_reference"],
  "status": "pass",
  "confidence": 0.93
}
```

## 4. Evidence Matrix Row

```json
{
  "task_id": "main_03",
  "spreadsheet_selling_point": "floral lace",
  "spreadsheet_status": "pass",
  "visible_source_fact": "source macro visibly shows the floral lace repeat",
  "decision_question": "What does the lace look like up close?",
  "visual_role": "lace_macro",
  "primary_source_id": "src_main_003",
  "secondary_source_ids": ["bulk_champagne_full", "bulk_champagne_print_close"],
  "selected_colours": ["Champagne"],
  "target_language": "ms-MY",
  "target_copy": {
    "headline": "Renda Bunga Yang Halus",
    "support": "Corak bunga yang ringan dan terperinci"
  },
  "claim_status": "pass",
  "gate_status": "pass"
}
```

## 5. Listing Plan JSON

`validate_listing_plan.py` expects this shape. Extra fields are allowed.

```json
{
  "product": "product-key",
  "source_language": "zh-CN",
  "target_language": "ms-MY",
  "selected_colours": ["Black", "Pink"],
  "set_policy": {
    "expected_main": 9,
    "min_detail": 4,
    "max_detail": 6,
    "max_flat_lay_main": 3
  },
  "tasks": [
    {
      "id": "main_01",
      "group": "main",
      "ratio": "1:1",
      "decision_question": "How does it look when worn?",
      "selling_point": "high-waist floral lace",
      "visual_role": "real_person_hero",
      "flat_lay": false,
      "contains_real_person": true,
      "preserve_body": true,
      "channel": "gemini-banana-pro-source-locked-edit",
      "colours": ["Black"],
      "target_copy": {
        "headline": "Renda Perancis Pinggang Tinggi",
        "support": ""
      },
      "claim_status": "pass",
      "evidence_status": "pass",
      "references": [
        {
          "path": "/absolute/path/source-model.jpg",
          "role": "real_person_source_lock"
        },
        {
          "path": "/absolute/path/bulk-black.jpg",
          "role": "exact_large_production_outer_product_colour_logo_reference"
        },
        {
          "path": "/absolute/path/print-close.jpg",
          "role": "exact_product_surface_print_reference"
        }
      ],
      "allowed_changes": ["remove Chinese", "target-language layout", "background cleanup"],
      "forbidden_changes": ["body regeneration", "new garment structure", "single-layer print"]
    }
  ]
}
```

### Plan gate requirements

- unique task IDs;
- main tasks use `1:1`; detail tasks use `9:16`;
- each task has one decision question and one selling point;
- each task has a visual/source-view reference;
- white-background anchors are never the sole reference;
- source files exist;
- selected colors are mapped and allowed;
- human tasks preserve the body and use a source-lock channel;
- claims have a status;
- complete-set counts and flat-lay limits pass;
- all evidence statuses are `pass`.

### SHENTAI Malay profile fields

Set `set_policy.profile` to `shentai-ms` and use `expected_main`, `min_detail`, and `max_detail` when the brief overrides its 8/9 defaults. Set `set_policy.virtual_model_master` to the approved master file’s path when virtual model images are requested. On those tasks set `contains_virtual_model: true` and include exactly one `virtual_model_identity_reference_only` pointing to that master. The master is a secondary input. It does not satisfy product evidence.

Tag original references on detail tasks with `source_family`: `source_detail`, `source_main`, `product_original`, `product_macro`, or `verified_data`. This tag describes provenance, independently of the reference’s visual role. A detail may use an earlier draft of the **same detail slot** for a targeted edit with original evidence attached. A finished main uses `generated_main` and cannot be supplied as a detail creation input. Use the original product sources to build an independently composed detail page.

## 6. Generation And Review Records

### Generation status

```json
{
  "id": "main_01",
  "channel": "gemini-banana-pro",
  "model": "actual-model-name",
  "request_status": "pass",
  "output": "/candidate/main_01.jpg",
  "attempts": [],
  "review_status": "pending"
}
```

### Multi-reference review

```json
{
  "id": "main_01",
  "status": "pass",
  "model": "actual-review-model-name",
  "product_issues": [],
  "body_issues": [],
  "colour_issues": [],
  "text_issues": [],
  "claim_issues": [],
  "recommendation_zh": ""
}
```

### Publish evidence

Record formal image/PDF paths, reviewed source directory, snapshot path, counts, dimensions, PDF pages, rendered sample paths, per-file SHA256, and exact comparison status.
