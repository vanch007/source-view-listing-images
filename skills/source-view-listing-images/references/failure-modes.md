# Failure Modes And Repairs

## Contents

1. Source and evidence failures
2. Plan and reference failures
3. Generation failures
4. Review failures
5. Publishing failures
6. Operational failures

## 1. Source And Evidence Failures

### Skipping deduplication and local recognition

- Symptom: later batches use unrelated or repeated files because only filenames were inspected.
- Root cause: planning began before a content index existed.
- Repair: hash, contact-sheet, OCR/VLM-describe, and role-tag every local source first. Keep a reversible duplicate manifest.

### Ignoring source-language marketing/detail images

- Symptom: outputs become generic white-background product renders and lose proven selling-point compositions.
- Root cause: source text was treated as unusable instead of translatable.
- Repair: use the marketing/detail image as `exact_layout_and_source_view_reference`; remove/translate its text while preserving the visual demonstration.

### Inferring color mapping

- Symptom: supplier files are assigned to spreadsheet color names by visual guess.
- Root cause: no mapping evidence.
- Repair: mark `missing evidence`, create an embedded-image confirmation board, and obtain user/supplier confirmation. Never infer the final mapping from model output.

### Treating text claims as physical proof

- Symptom: a prompt generates antibacterial, shaping, support, fragrance, or medical results that pixels and documents do not prove.
- Root cause: source copy and visible facts were merged.
- Repair: separate `source_text_claim` from `visible_proof`; mark `claim_evidence_pending`; use non-absolute copy or omit the claim.

## 2. Plan And Reference Failures

### White-background image as creative primary

- Symptom: many outputs are the same product on different backgrounds.
- Root cause: a fidelity anchor was assigned as a selling-point source.
- Repair: bind a demonstrated marketing/detail image as primary; keep white/transparent images secondary for structure and color verification.

### Reference unrelated to the selling point

- Symptom: candidate and source have no meaningful visual connection.
- Root cause: sources were selected by product ID only, not by decision question.
- Repair: require `selling point -> visible fact -> decision role -> exact source` in the evidence matrix.

### Detail-only reference defines the whole product

- Symptom: generated product has the wrong silhouette or structure.
- Root cause: only a gusset, strap, print, or material close-up was supplied.
- Repair: add an exact full-product reference; limit the close-up role to its visible detail.

### Data reference overrides product truth

- Symptom: size/composition card contains a generated wrong product.
- Root cause: a data card was the only reference.
- Repair: bind both exact whole-product references and data-only references. State that data controls text only.

### Outer and inner construction are conflated

- Symptom: an internal X, gusset, lining, or support panel appears as a dark external surface feature.
- Root cause: transparent/internal topology reference was allowed to control appearance.
- Repair: label it `inner_topology_reference_only`; use bulk photos for outer appearance; require same-tone weak visibility except in explicit structure diagrams.

### Flat-lay dominated set

- Symptom: individually acceptable images still feel repetitive and fail as a Listing.
- Root cause: no set-level purchase-decision role gate.
- Repair: design the entire set first; cap flat-lay mains; require human/use, macro, structure, color, fit, and data roles where evidence permits.

## 3. Generation Failures

### Local collage/crop presented as final AI image

- Symptom: stitched panels have visible crop seams and lack coherent design.
- Root cause: local composition substituted for model generation/editing.
- Repair: use local work only for contact sheets/evidence; send the source-locked task to the approved image model for the final canvas.

### Real body or garment is regenerated

- Symptom: new torso/limbs, altered face, different pose, changed garment boundary, or obvious crop extension.
- Root cause: a generative prompt treated the person as scene material.
- Repair: route to source-locked human-image editing, explicitly forbid body extension, and require SIFT/RANSAC plus visual review. Reject rather than rationalize.

### Physical logo/print is missing, single-layer, or misspelled

- Symptom: bulk waistband or packaging print differs from the physical item.
- Root cause: model received only a full product or generic logo board.
- Repair: provide full product plus exact print close-up; specify spelling, layers, overlap, contrast, and orientation. Regenerate only affected slots.

### Official Listing logo is hallucinated

- Symptom: distorted brand mark or inconsistent placement.
- Root cause: logo was requested during generation.
- Repair: leave continuous background at the approved corner, audit the raw candidate, then overlay the official transparent asset locally on mains only.

### Wrong number of colors/products

- Symptom: five-color card shows six or seven products, or an allowed color drifts to navy/another SKU.
- Root cause: group reference or prompt was underspecified.
- Repair: bind each selected color to one exact bulk reference and label them explicitly; require exact count and run visual review against all references.

### Target-language or data corruption

- Symptom: mixed-language composition, pseudo text, wrong sizes, or misspelled color names.
- Root cause: free-form prompt and no text gate.
- Repair: provide exact required strings, use a text-only source-locked edit, and review rendered text separately from product fidelity.

### Output ratio is wrong

- Symptom: a main image is vertical or detail image is square.
- Root cause: channel defaults or missing ratio in manifest.
- Repair: encode ratio per task and run deterministic aspect-ratio audit before visual review.

## 4. Review Failures

### API success is treated as image success

- Symptom: request status says `pass`, but product or text is wrong.
- Root cause: transport status and review status share one field.
- Repair: store `request_status` and `review_status` separately. Only the latter can authorize selection.

### Reviewer receives the wrong reference role

- Symptom: a local model returns `pass` because it compared a texture/detail source to a whole product it could not validate.
- Root cause: reference role was implicit or incorrect.
- Repair: send all controlling references with explicit roles and role-specific instructions. Reopen any historical pass based on the wrong source.

### Single-image fidelity hides set-level repetition

- Symptom: 13/13 fidelity passes but the Listing repeats the same view.
- Root cause: no whole-set review.
- Repair: run pHash, visual-role counts, primary-source reuse, decision-question coverage, and manual contact-sheet review.

### Text issues are hidden by product pass

- Symptom: product is faithful but Malay/target text is malformed.
- Root cause: reviewer was told to ignore text.
- Repair: keep product fidelity and text quality as separate fields; both must pass before publication.

## 5. Publishing Failures

### PDF lists paths instead of showing references

- Symptom: user cannot visually compare source and candidate.
- Root cause: report contains filenames only.
- Repair: embed every reference thumbnail, label its role, and render-sample the PDF.

### Formal files are overwritten without recovery

- Symptom: old accepted/rejected state cannot be audited or restored.
- Root cause: direct copy into the formal directory.
- Repair: snapshot images and PDF first, then publish reviewed files and verify SHA256.

### Stale project status contradicts final evidence

- Symptom: one document says `missing evidence` while another says `pass`.
- Root cause: completion did not include documentation audit.
- Repair: search status/memory for stale conclusions, update canonical status, and keep historical failures clearly marked `rejected` or superseded.

## 6. Operational Failures

### Slow, quota-limited, or disconnected channel

- Symptom: 429, 503, timeout, remote disconnect, or output download failure.
- Root cause: account quota, network, or long-running generation.
- Repair: retain task IDs and attempt logs; retry transient failures; batch approved tasks within one product; switch fallback only after evidence. Do not change the plan because of a transport failure.

### Unbounded parallel generation

- Symptom: multiple products finish with inconsistent references and no review bandwidth.
- Root cause: concurrency optimized request speed instead of product closure.
- Repair: parallelize human and non-human channels only within the same fully planned product; finish review/PDF/publish before moving to the next product.

### Model capability assumption becomes policy

- Symptom: a route is changed because one model happened to work or fail once.
- Root cause: anecdote was recorded as fact.
- Repair: label capability hypotheses `pending`; change routing only after category-specific comparison evidence.
