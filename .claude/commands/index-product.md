# Index a Product into the Product Library

Turn a finished, hand-built product deck (a dedicated Figma page of polished slides)
into a reusable **product pack** the generator can clone-and-rewrite. Generates the
`products/registry.json` entry *from* what was built in Figma — the Figma page is the
source of truth; the registry is a generated mirror.

## Usage
```
/index-product <slug-or-figma-page-url>
```
- `<slug>` — an existing product slug (re-index/update), resolved to its `pageId` from `products/registry.json`.
- A Figma page/node URL — parse the `node-id` for a new product page.

Mirrors the "Adding New Templates" flow in `CLAUDE.md`, but for finished product slides.

## Important: Load the figma-use skill
Before calling any `use_figma` MCP tool you MUST invoke the `figma:figma-use` skill. Mandatory every session. Always pass `skillNames: "figma-use"` to `use_figma`.

## Reference docs (read first)
- `docs/superpowers/specs/2026-05-30-product-content-library-design.md` — the design (decisions, data model).
- `products/registry.json` — existing product packs (match the shape exactly).
- `assets/library.json` — image index (you will extend it).
- `templates/design-system.md` — the semantic layer-name convention you must follow.

---

## Step 1: Resolve the product page
- Slug → look up `products.<slug>.pageId` in `products/registry.json`.
- URL → extract `fileKey` (`GkUiwJTK5Xi65AKw4MOjTL`) and the page/frame `node-id`.
- Confirm the product `displayName` and `slug` (kebab-case) with the user if new.

## Step 2: Read every slide frame
- `get_metadata` on the page to list the slide frames (top-level frames, left→right by x).
- For each frame, read its text nodes' **id + name + characters** (a read-only `use_figma`
  scan returning `{id, name, characters}` is cleaner than `get_design_context`'s code dump).
- When a slide's purpose is ambiguous, `get_screenshot` it before deciding role/slots.
  **Do not guess from layer names alone** — confirm content visually when unsure.

## Step 3: Apply the semantic naming convention
Rename each slide **frame** to a unique `slug-descriptor` name (e.g. `purifier-profile-cleone`),
and rename **content-named text nodes** to slot roles. Use the existing vocabulary — do NOT invent synonyms.

**Keep as-is** (already semantic): `title`, `body`, `heading`, `caption`, `eyebrow`,
`cell-heading-N`, `cell-body-N`, `bullet-heading-N`, `bullet-body-N`, `meta-left`,
`meta-right`, `meta-top-right`.

**Rename content-named text nodes** (a node whose name == its own text) to:
- Product name → `product-name`; product tagline/descriptor → `product-desc`
- Big stat number → `stat-value`; stat prefix ("Up to") → `stat-prefix`; stat caption → `stat-label`
  - Multiple stats on one slide → number them: `stat-value-1`, `stat-label-1`, `stat-value-2`, …
- Small section label above a block → `eyebrow` (second one → `eyebrow-2`)
- A heading/method name used as a block heading → `heading`
- Block prose → `body` (second one → `body-2`); continuation of a split title → `title-2`
- A trailing ™/® split-glyph node named `title`/`heading` → `title-trademark` / `heading-trademark`
- Comparison-table: product column headers → `col-heading-N`; the empty top-left header → `row-label-header`;
  row labels (left column) → `row-label-N`; data cells → `cell-<row>-<col>`
- A labeled diagram's repeated label/value pairs → `<diagram>-label-N` / `<diagram>-spec-N` (e.g. `spectrum-label-1`)

**Leave untouched** (the generator never targets these): decorative shapes/groups
(`Ellipse N`, `Line N`, `Vector`, `Group N`, `Frame NNNN`, `Clip path group`, rings),
image-bearing nodes whose name is a render filename (handled in Step 4), `meta-*` chrome,
and decorative brand wordmark text (rename those to `wordmark` / `wordmark-2` only so they
stop reading as content — they are not registry content slots).

**Show the user the proposed `{nodeId: newName}` map and apply after confirmation**, via one
`use_figma` batch:
```js
const renames = { /* nodeId: "newName", ... */ };
const failed = [];
for (const [id, name] of Object.entries(renames)) {
  const n = await figma.getNodeByIdAsync(id);
  if (n) { n.name = name; } else { failed.push(id); }
}
return { renamedCount: Object.keys(renames).length, failed };
```
**Verify:** re-scan each frame; assert no text node's `name` equals its own rendered text.

## Step 4: Index product images
- Find image-bearing nodes (nodes with an `IMAGE` fill) under each slide. Guard against
  `GROUP` nodes (they throw on `.fills`) — filter by node type first.
- Deduplicate by visual subject; pick the cleanest/largest source node per subject.
- Add each to `assets/library.json` `assets` with an **SEO-friendly key** (lowercase,
  hyphen-separated, brand keywords — content-descriptive, since these go on the web):
  `{ "nodeId": "...", "tags": ["product", "<slug>", ...], "description": "..." }`.
- If an image's subject can't be confirmed without exporting, **skip it and note it** rather
  than mislabel it.

## Step 5: Assign role + matchHints per slide
Use the **controlled role vocabulary** (extend only when a product genuinely needs a new role; never fork synonyms):
```
hero · key-specs · how-it-works · value-prop · comparison · pricing · sustainability · use-case · cta
```
For each slide propose `role` + a one-sentence `matchHints` (what incoming-slide intent it
covers). **Confirm with the user**, then assemble the `slots` map from the captured slot text
(content slots only — omit `meta-*`, `wordmark*`, and `*-trademark`).

## Step 6: Write the registry entry
Write/replace `products.<slug>` in `products/registry.json`, matching the existing shape:
```jsonc
{
  "displayName": "...",
  "pageId": "<page node-id>",
  "aliases": ["...", "..."],        // distinctive detection terms; AVOID generic single words
                                     // (e.g. "pro", bare "spirit") that false-match unrelated decks
  "slides": [
    { "role": "...", "nodeId": "...", "frameName": "...", "matchHints": "...", "slots": { "...": "..." } }
  ],
  "content": { "valueProps": ["..."], "keySpecs": ["..."] },   // verified facts for thin PDFs
  "images": [ { "assetKey": "<key in assets/library.json>" } ]
}
```

## Step 7: Validate (must end green)
Run and report:
```
python3 tools/validate_products.py
```
Expected: `OK — N products, M slides`. If it prints `FAIL`, fix the listed errors before finishing.

## Step 8: Report
Summarize: product slug, # slides indexed (with role each), # images added, validator result.
Note anything skipped or any role/name you were unsure about so the user can adjust.

## Notes
- **Additive & non-destructive.** Renaming layers changes no pixels. Never delete nodes; if a
  duplicate/stale page exists, move it to a review page rather than deleting.
- Node IDs survive page moves, so a product can later move to its own page with a one-field
  `pageId` change — no re-index.
- Do NOT use `figma.notify()` / `console.log()` for output; do NOT wrap code in an async IIFE;
  switch pages with `await figma.setCurrentPageAsync(page)`.
