# Multilingual Listing Image SOP

## Contents

1. Scope and inputs
2. Source indexing and reversible deduplication
3. Spreadsheet and source-image fact extraction
4. Evidence matrix
5. Complete-set design
6. Target-language copy
7. Generation routing and prompts
8. Candidate review and repair
9. Documentation and publishing
10. Completion audit

## 1. Scope And Inputs

Use this SOP when the available material includes any combination of:

- a verified product brief, original size sheet, or spreadsheet covering SKU facts and claims;
- source-language marketing/detail images with text and useful visual demonstrations;
- exact bulk product photos, color samples, close-ups, white-background images, or transparent structure images;
- a specified real model photo or an approved virtual model master;
- existing Listing images that need repair in another language.

For the brand-specific Malay flow, follow [SHENTAI Malay Listing](shentai-malay-listing.md) for counts, portrait sequencing, virtual identity handling, and local archive.

Read project rules and existing status before touching files. Preserve current formal images until publication is authorized and all gates pass.

Create one working directory per product. Never generate different products concurrently.

## 2. Source Indexing And Reversible Deduplication

Inventory every source directory before planning:

- absolute path and stable source ID;
- dimensions, aspect ratio, file size, SHA256, and perceptual hash;
- exact duplicate group and near-duplicate group;
- source family: main, detail, bulk, color, close-up, transparent, spreadsheet-embedded, old SKU, or generated;
- people/hands/body crop;
- product view and visible region;
- visible color, material, construction, print/logo, and selling-point demonstration;
- source text/OCR and language;
- confidence and evidence status.

Do not delete duplicates during the audit. Move or remove them only after a manifest and snapshot exist. Prefer a canonical source plus duplicate pointers.

Build contact sheets with readable thumbnails and source IDs. A Markdown table must embed actual images when the user needs visual confirmation; paths alone are not a visual review.

## 3. Spreadsheet And Source-Image Fact Extraction

### Spreadsheet authority

Use a structured spreadsheet parser. Extract only the selected product row and selected SKU scope:

- allowed colors and any supplier color mapping;
- sizes and size semantics;
- material composition and component names;
- construction/features;
- approved claims and evidence state;
- product code and naming.

Do not turn an embedded spreadsheet image into proof of an unseen color or structure. Record ambiguous cells as `pending` or `missing evidence`.

### Source-language detail images

Use OCR and visual recognition together. For each image, separate:

- **source text claim**: what the Chinese/source-language text says;
- **visible proof**: what the pixels visibly demonstrate;
- **visual role**: model wear, hand stretch, macro texture, construction diagram, color group, size card, comparison, packaging, or lifestyle;
- **candidate use**: layout reference, exact source view, product truth, data only, or style only.

Text can suggest a selling point but cannot prove a physical fact that is not visible or independently documented.

### Bulk product evidence

Use full-product bulk images to lock:

- silhouette and proportions;
- outer versus inner construction;
- selected color;
- fabric and trim;
- straps, gusset, closures, seams, hardware;
- physical waistband/packaging print.

Use close-ups only for the detail they show. A close-up cannot define the whole product.

## 4. Evidence Matrix

Create one row per proposed output slot:

`spreadsheet selling point -> visible source fact -> purchase-decision question -> visual role -> primary source -> product/data references -> target-language copy -> claim status -> gate status`

Apply the authority order from `SKILL.md`. When two sources conflict:

1. state the conflict;
2. identify which authority each source holds;
3. request or locate missing evidence;
4. keep the slot blocked until resolved.

Do not “average” conflicting products or let a generated candidate resolve the conflict.

Use the schemas and reference roles in `evidence-schema.md`.

## 5. Complete-Set Design

Design the full set before any generation. For apparel, default to:

- 9 square main images;
- 4–6 vertical information/detail images;
- target language dominant;
- one image, one selling point.

Assign purchase-decision roles, for example:

- hero/full product or model wear;
- selected colors;
- material/texture;
- construction or closure;
- fit/coverage;
- real-person comfort or movement;
- feature demonstration;
- size/data;
- vertical feature summary;
- vertical macro, process, or usage detail.

Reject a plan if it is dominated by flat lays, white-background products, repeated front views, repeated titles, or the same decision question. Changing background or color does not create information gain.

White-background and transparent images are fidelity anchors. They may become a creative primary only when the selling point itself is a clean product/structure inspection and no better demonstrated source exists.

For every slot, state:

- what remains exactly unchanged;
- what may change;
- which reference controls layout/view;
- which reference controls product truth;
- which reference controls data;
- which reference controls style only;
- what must not appear.

Run `validate_listing_plan.py` before generation.

## 6. Target-Language Copy

Translate meaning, not source-language hype. Keep the target language dominant and concise.

Rules:

- for main images, one headline and at most one short support line by default; detail panels may include captions and supporting information needed for their purchase-decision role;
- preserve exact sizes, percentages, color names, and component names;
- use exact strings in prompts for data cards;
- do not include internal product codes, random pseudo text, source platform text, QR codes, or Chinese unless requested;
- avoid absolute, therapeutic, guaranteed, or result-oriented wording;
- mark antibacterial, HPV, fragrance, shaping, support, certification, or performance claims `claim_evidence_pending` until evidence is verified;
- distinguish a language-quality problem from a product-fidelity problem.

After generation, review rendered text. An API may return an image while misspelling a brand, color, size, or composition. Repair text-only failures with a source-locked edit that preserves the approved pixels.

## 7. Generation Routing And Prompts

### Channel routing

Honor the user’s explicit model choice. If no override exists and the project supports them:

- non-human images: GPT Image 2 complete generation/edit;
- human or real-hand references: Gemini Banana Pro source-locked edit;
- slower fallback channels: only after primary-channel failure/quota evidence is recorded.

Treat model capability assumptions as `pending` until validated on the current product category. Do not assume a model that handled a bra can safely handle underwear on a real body.

Two channels may run concurrently for the same product after the complete plan passes. Do not generate multiple products concurrently.

### Prompt contract

Use explicit reference roles:

```text
Reference 1 controls the exact source view, composition, and visible selling-point demonstration.
Reference 2 controls the exact bulk product silhouette, color, material, and construction.
Reference 3 controls only the physical print/logo close-up.
Reference 4 controls only verified size/composition data.

Preserve all product-critical pixels and facts from their controlling references.
Translate/remove source text and build the requested target-language Listing layout.
Do not invent unseen angles, colors, body parts, packaging, props, structure, claims, or text.
If references conflict, preserve the higher-authority product evidence and simplify the design.
```

For human images add:

```text
Preserve the original face, body, pose, hands, crop, anatomy, and garment boundaries.
Do not extend or regenerate the body. Edit only the requested product print/text/layout/background.
```

For physical product print/logo add a full-product and close-up reference. Describe the exact layer count, placement, spelling, contrast, and orientation. Do not use a logo board alone to define the product.

For official Listing brand logos, ask the model to leave clean continuous background in the final placement area. Overlay the transparent asset only after review.

### Request evidence

Store per-task request status, channel/model, inputs, prompt, output path, task ID when available, account/fallback attempts, and errors. Use a practical timeout such as 180 seconds where supported.

Retry transient network failures without changing the approved plan. Regenerate only failed slots. Request `pass` means only that an output file exists.

## 8. Candidate Review And Repair

Review in this order:

1. file exists, correct ratio and dimensions;
2. single-image product fidelity against all controlling references;
3. selected color and physical print/logo;
4. real-person/hand source lock with visual review plus SIFT/RANSAC;
5. target-language text and exact data;
6. claim safety;
7. complete-set role coverage and information gain;
8. pHash near-duplicates.

Use `local_visual_review.py` for multi-reference comparison and `audit_listing_set.py` for deterministic set checks.

When a candidate fails:

1. name the violated fact;
2. identify the incorrect reference role or prompt phrase;
3. repair the plan/binding, not only the prose prompt;
4. preserve passed candidates;
5. regenerate only the failed task;
6. rerun single-image and whole-set audits.

Never normalize away a real mismatch because a model returned `pass`.

## 9. Documentation And Publishing

After all raw candidates pass:

1. overlay the approved transparent logo on main images only unless instructed otherwise;
2. verify the logo does not cover product, title, or data;
3. build a PDF with one cover plus one page per final image;
4. embed every actual reference image and label its role; do not list paths as a substitute;
5. include final candidate, review status, model name, claim state, and logo note;
6. render-sample cover, first image, a dense multi-reference page, and final page;
7. snapshot the existing formal image directory and existing PDF;
8. publish only the reviewed files;
9. compare reviewed-to-formal SHA256 for every image and PDF;
10. write final audit and publish evidence.

Do not delete an old source batch or old formal version merely because a new version passes. Keep it as a snapshot or rejected history unless the user authorizes deletion.

## 10. Completion Audit

Mark the product `pass` only when every required artifact and review is closed. Mark the larger goal complete only when every product is independently `pass` and the formal directory/PDF inventory matches the final status table.

Update project status and memory with only reusable facts: routes, model, final status, evidence paths, known failure modes, and next product. Remove or supersede stale contradictory conclusions.
