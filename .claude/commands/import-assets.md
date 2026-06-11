# Import Assets from SharePoint

Search the synced SharePoint library for brand imagery, curate it visually in Figma, and index the keepers into `assets/library.json` (v2 schema).

## Usage
```
/import-assets <search terms | folder path>
```

## Fetch path
<!-- Spike result: docs/superpowers/specs/2026-06-11-import-spike-result.md -->
The MS365 MCP **cannot fetch image binaries** (images are not indexed in `sharepoint_search`; folder listings return names without URIs). Binaries come from the **locally synced library**:

```
~/Library/CloudStorage/OneDrive-SharedLibraries-BluewaterGroup/Marketing - Documents/
```

This mirrors the SharePoint `Marketing2024` site tree exactly. `cp` transparently downloads cloud-only files. `source.type` for these imports: `"onedrive-sync"`; `source.path` is the path relative to `Marketing - Documents/`.

## Important: Load skills and tools first
- Invoke the `figma:figma-use` skill before any `use_figma` call (mandatory).
- Load Figma tools in ONE ToolSearch call: `select:mcp__figma__use_figma,mcp__figma__get_screenshot,mcp__figma__upload_assets`

## Process

### Step 1: Find candidates
**Where to look first:** the team's primary image source is `Product Categories/` — especially `Product Categories/Bluewater Stations/` and `Product Categories/Bluewater Purifiers/` (per Jens, 2026-06-11). Sibling folders under `Product Categories/` and the `Distributor Folder/Content (Images, Videos and Renders)/` tree are secondary. Prefer `Product Categories` when the same file appears in both.

**Watch for stale product designs:** folders named `Old <product>` (e.g. `Spirit/Content/Renders/Old Spirit/`) mark previous-generation casings. The same files often ALSO sit unmarked in the Distributor tree. When an import candidate matches an `Old *` folder's contents, say so during curation and note it in the asset description.

Search the synced tree with the user's terms — filenames AND folder names, images only:

```bash
SYNC_ROOT=~/Library/CloudStorage/OneDrive-SharedLibraries-BluewaterGroup/"Marketing - Documents"
find "$SYNC_ROOT" \( -iname "*<term>*.jpg" -o -iname "*<term>*.jpeg" -o -iname "*<term>*.png" -o -iname "*<term>*.webp" \) -not -path "*/.*" 2>/dev/null
# Also try term as a folder: find "$SYNC_ROOT" -type d -iname "*<term>*", then list images inside.
```

Drop files under 50 KB (icons/thumbs — `_thumb` suffixes especially) unless the user asked for them.

**Dedupe:** read `assets/library.json`; drop any candidate whose `Marketing - Documents/`-relative path matches an existing `source.path`. **Also dedupe by basename + byte size**: the same image frequently lives in several folders (verified: the Spirit render set exists in both the Distributor tree and `Old Spirit/`), so compare each candidate's filename and `stat -f%z` size against already-imported sources and against the other candidates in this batch. List skipped duplicates in the final report only — do not re-offer them.

If more than ~12 candidates remain, show the user the file list grouped by folder and ask which subset to stage (staging all of a huge result wastes uploads). If zero remain, report that and stop.

### Step 2: Fetch binaries
Copy each remaining candidate to a temp dir (filenames may repeat across folders — prefix with a counter: `01-<name>.jpg`). Verify each with `file` (must report an image; discard zero-byte or non-image files).

**Downscale oversized files (REQUIRED):** `upload_assets` rejects files over 10 MB, and master renders routinely exceed it (verified: 7680×4800 PNGs at 21–75 MB). For any file over 10 MB or wider than 3000px:
```bash
sips -s format jpeg -s formatOptions 90 -Z 3000 "<file>.png" --out "<file>.jpg"
```
3000px comfortably covers full-bleed slide use (1920px). Keep PNG only when the image needs transparency (check with `sips -g hasAlpha`); otherwise JPEG at 90.

### Step 3: Stage the Import inbox in Figma
1. `upload_assets` in batches of ≤5 (its max per call); POST each file multipart: `curl -s -X POST -F "file=@<path>;type=image/<jpeg|png|webp|gif>" "<submitUrl>"`. The filename becomes the layer name; record each returned `placedOnNodeId`.
2. **Uploads land as 400×300 frames on the file's CURRENT page** — not Brand Assets. In ONE `use_figma` pass: switch to the Brand Assets page (`51124:14`), then for every uploaded node: move it to that page, resize to the image's native aspect at 480px width (`n.resize(480, 480 * origH / origW)` — read the fill image's dimensions via `figma.getImageByHash(fill.imageHash).getSizeAsync()`), and arrange the grid: 4 per row, 48px gaps, placed to the RIGHT of existing content (`maxX + 96`). Wrap all cards in a frame named `Import inbox — <date>`, and give each card a label text node above it (`A1`, `A2`, … + the source filename at 14px gray).

### Step 4: Curate (visual keep/skip)
`get_screenshot` the inbox frame and show it. Ask the user which to keep via AskUserQuestion (multiSelect over the labels) or accept free-form "keep A1, A3, B2". **Never ask the user to judge by filename/path/size — the screenshot is the decision surface.**

### Step 5: Index keepers, delete skips
For each keeper:
1. Rename the node to a kebab-case SEO-style asset key (descriptive: subject-product-context, e.g. `spirit-purifier-kitchen-lifestyle`). Move it out of the inbox frame onto the Brand Assets page layout.
2. Measure rendered `width`/`height` → `visual.aspect` (2 decimals), derive `orientation` (square = 0.9–1.1).
3. `get_screenshot` the node and write from what you SEE: a one-sentence visual `description`, `tags`, `tone` (light/dark/mixed), `subject` (center/left/right/top/bottom), `suitability` (subset of hero/full-bleed/card/detail/texture — full-bleed needs atmospheric width AND high quality), `quality` (high/medium/low — judge from the native pixel size recorded at upload plus visible sharpness).

Delete every skipped node, then delete the empty inbox frame. Return all mutated node IDs.

### Step 6: Write the library and validate
Add each keeper to `assets/library.json` under `assets`:
```json
"<asset-key>": {
  "nodeId": "<figma node id>",
  "tags": ["..."],
  "description": "...",
  "source": { "type": "onedrive-sync", "path": "<path relative to Marketing - Documents/>", "importedAt": "<YYYY-MM-DD>" },
  "visual": { "aspect": 0.0, "orientation": "...", "tone": "...", "subject": "...", "suitability": ["..."], "quality": "..." }
}
```
Run `python3 tools/validate_assets.py` — must end `OK`. If it fails, fix the entries and re-run; never leave the library red.

### Step 7: Report
```
Import complete.
Searched: "<terms>" — N candidates (M duplicates skipped)
Kept: K assets
  - spirit-purifier-kitchen-lifestyle (landscape 1.50, light, hero/full-bleed/card)
  - ...
Skipped: N-K (deleted from Figma)
Library: python3 tools/validate_assets.py → OK — <total> assets
```

## Notes
- The MS365 MCP (`sharepoint_folder_search`) may still help DISCOVER folder paths by name when the user describes a folder rather than a filename — but all bytes come from the synced tree.
- If the synced tree is missing (no `~/Library/CloudStorage/OneDrive-SharedLibraries-BluewaterGroup`), stop and ask the user to sync the Marketing library in OneDrive first.
