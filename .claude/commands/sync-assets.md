# Sync Brand Assets

Scan the "Brand Assets" page in Figma and update the local asset library (v2 schema). New assets are vision-indexed automatically; the user confirms or adjusts the metadata rather than authoring it from scratch.

## Usage
```
/sync-assets
```

## What it does

1. Reads `assets/library.json` to get the Brand Assets page ID
2. Uses `get_metadata` to scan all frames/rectangles on that page
3. For each named node that has an image fill, detects whether it is new or already in the library
4. Vision-indexes each NEW asset (screenshot → measure → describe) and asks the user to confirm/adjust
5. Writes the updated `assets/library.json` (existing assets keep their `visual`/`source` untouched)
6. Validates the library and reports

## Process

### Step 1: Read current library

Read `assets/library.json` from the project root. Note the `assetPageId` and all existing asset keys (so existing entries are never overwritten).

### Step 2: Scan the Brand Assets page

Use `get_metadata` with the `assetPageId` and `fileKey` from `templates/registry.json` to list all children on the Brand Assets page.

Collect every frame or rectangle that is a direct child of the page (skip the instruction text node). Record:
- `name` (the layer name the user gave it)
- `nodeId`

### Step 3: Detect new vs existing assets — vision-index new assets

Compare the scanned nodes against existing assets in `library.json`.

**Existing assets:** keep their current `visual` and `source` blocks untouched. No re-indexing.

**New assets:** for each new node, run the vision-index procedure:
1. `get_screenshot` the node.
2. Measure the rendered `width` and `height` via `use_figma` → compute `visual.aspect` = width ÷ height, rounded to 2 decimals. Derive `orientation`: square = 0.9–1.1; landscape > 1.1; portrait < 0.9.
3. From what you SEE in the screenshot, write:
   - `description` — one sentence describing the image
   - `tags` — kebab-case array (suggest from name + content)
   - `tone` — `light` / `dark` / `mixed`
   - `subject` — primary subject position: `center` / `left` / `right` / `top` / `bottom`
   - `suitability` — non-empty subset of `hero` / `full-bleed` / `card` / `detail` / `texture` (full-bleed needs atmospheric width AND high quality)
   - `quality` — `high` / `medium` / `low` (judge from visible sharpness)

After indexing all new assets, show the user the proposed metadata for each and ask them to confirm or adjust via AskUserQuestion. Apply any corrections before writing.

### Step 4: Update library.json

Write the updated `assets/library.json` with all assets (existing + new).

**Existing assets** are written back exactly as read — their `visual` and `source` blocks must not change.

**New (figma-sourced) assets** use this v2 entry format:
```json
"<asset-key>": {
  "nodeId": "<figma node id>",
  "tags": ["..."],
  "description": "...",
  "source": { "type": "figma" },
  "visual": {
    "aspect": 0.0,
    "orientation": "landscape|portrait|square",
    "tone": "light|dark|mixed",
    "subject": "center|left|right|top|bottom",
    "suitability": ["hero", "card"],
    "quality": "high|medium|low"
  }
}
```

Note: figma-sourced entries carry `"source": { "type": "figma" }` — no `path` or `importedAt`.

### Step 5: Validate and report

Run `python3 tools/validate_assets.py` — must end `OK`. If it fails, fix the entries and re-run; never leave the library red.

Show the user what was synced:
```
Asset library synced!

Existing: 3 assets (unchanged)
New: 2 assets added
  - cafe-station-1-angle (landscape 1.50, light, hero/card)
  - sustainability-ocean (landscape 1.78, mixed, hero/full-bleed)

Total: 5 assets in library
python3 tools/validate_assets.py → OK — 5 assets, 0 preference records
```
