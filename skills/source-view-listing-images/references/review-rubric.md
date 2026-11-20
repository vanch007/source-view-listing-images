# Listing Review Rubric

## Contents

1. Review layers
2. Single-image product fidelity
3. Human and hand preservation
4. Text, data, and claims
5. Whole-set information structure
6. Logo, PDF, and publishing
7. Status and repair rules

## 1. Review Layers

Run separate gates. One gate cannot excuse another:

1. request/file gate;
2. ratio/dimension gate;
3. single-image product-fidelity gate;
4. human/hand preservation gate;
5. target-language/data/claim gate;
6. whole-set role and duplicate gate;
7. logo/PDF/publish gate.

Record the actual reviewer model name. A request result is evidence only for transport/output existence.

## 2. Single-Image Product Fidelity

Compare the candidate with every controlling reference and its declared role.

`pass` requires:

- exact product category and selected SKU;
- correct silhouette, proportions, view, crop, and visible region;
- correct color mapping;
- correct material pattern, seams, trim, gusset, straps, hardware, closure, packaging, and physical print where visible;
- layout/view reference retained as intended;
- data/style references not overriding product truth;
- internal topology not converted into an external feature.

`fail` examples:

- wrong whole product generated from a close-up;
- extra products, colors, packaging, props, body parts, straps, or closures;
- missing or misspelled physical print/logo;
- changed product angle without evidence;
- external dark X generated from a same-tone internal X;
- a white-background product substituted for the demonstrated selling-point view.

`pending` when resolution, crop, or conflicting references prevent a reliable decision.

## 3. Human And Hand Preservation

For source-locked real-person or real-hand edits:

- visually compare face, body, pose, hands, anatomy, crop, lighting boundaries, and garment edges;
- run SIFT/RANSAC against the original source;
- reject generated extensions, changed anatomy, new pose, new body region, garment redraw, or obvious crop seams;
- do not treat a high feature-match count as permission to ignore a visible body error;
- do not require SIFT for fully generated non-human scenes.

Keep thresholds project-specific. Store good matches, RANSAC inliers, algorithm parameters, and status. For virtual-model scenes, compare all relevant views with the approved identity master and verify consistent face, hair and proportions across the set. A planned new virtual pose is not a modification of a real locked source.

## 4. Text, Data, And Claims

Review target-language text separately:

- target language is dominant;
- headline is readable and relevant to the one selling point;
- no source-language remnants unless requested;
- no random pseudo text, internal SKU, platform, QR code, or hallucinated certification;
- color names, sizes, units, percentages, and material names exactly match verified facts;
- physical brand spelling is exact;
- no absolute, therapeutic, guaranteed, or unsupported result wording;
- sensitive claims retain `claim_evidence_pending` or verified evidence status.

A faithful product with malformed text is not publishable. AI may generate target-language typography directly inside the finished image; review every rendered word, number, unit, and material value. Regenerate the same slot when typography fails. When the user requests a stronger visual redesign, allow AI to rebuild the surrounding composition while the declared exact-product references remain authoritative.

For a dedicated colour-selection image, bind every displayed colour name to its corresponding product image or swatch. Listing the names only in a headline is `fail`. A single-colour hero, structure, material, or wearing image does not need a colour label unless colour identification is that slot's declared decision role.

## 5. Whole-Set Information Structure

Review a contact sheet plus plan metadata.

Require:

- expected main/detail counts and ratios;
- distinct purchase-decision questions;
- one selling point per image;
- useful mix of full product/model, color, material, construction, fit/use, feature demonstration, and size/data roles as evidence permits;
- no flat-lay or white-background dominance;
- no repeated primary view disguised by background/title changes;
- pHash near-duplicate count 0 at the configured threshold;
- visible information gain from each detail image;
- selected colors only.

When a user identifies one or more bad images, expand the review to every image in that product set. The named images are examples of failure, not the complete repair scope. Recheck every main and detail slot for missing copy, missing selling-point explanation, colour binding, design quality, information gain, and source fidelity before accepting the set.

Treat low pHash distance as a review trigger, not the sole semantic decision. Two structure pages can be perceptually similar yet distinct; two differently colored versions can be semantically duplicate despite a larger distance.

## 6. Logo, PDF, And Publishing

Raw candidate review occurs before official transparent logo overlay.

After overlay require:

- logo uses the approved asset;
- main-only/detail policy is followed;
- logo does not cover product, title, data, face, or hands;
- PDF embeds all references and candidates at readable size;
- each reference role is labeled;
- PDF page count equals cover plus final image count;
- rendered sample pages are nonblank and not clipped;
- snapshot exists before replacement;
- formal files match reviewed files by SHA256;
- old versions are retained or explicitly deleted with authorization.

## 7. Status And Repair Rules

Use:

- `pass`: all evidence for this gate is closed.
- `fail`: a visible or deterministic requirement is violated.
- `pending`: review remains inconclusive or incomplete.
- `missing evidence`: required truth source is absent.
- `rejected`: superseded candidate/version that cannot be selected.

On failure, patch the source binding or role before changing prompt adjectives. Regenerate only failed slots and rerun both single-image and set-level gates.

Do not normalize a reviewer’s contradictory numeric/text response. Rerun or escalate to human review.

A direct user acceptance is the human-review gate for that reviewed version. Preserve it as `pass` evidence and do not let a later machine-only style suggestion silently reverse it. A later higher-authority factual conflict may reopen the slot, but the report must name that evidence and use `pending` until resolved.

## Multi-Reference VLM Output

Require JSON fields:

```json
{
  "status": "pass|fail|pending|missing evidence",
  "summary_zh": "",
  "product_issues": [],
  "body_issues": [],
  "colour_issues": [],
  "text_issues": [],
  "claim_issues": [],
  "recommendation_zh": ""
}
```
