# Image Pipeline — SharePoint Import + Vision-Indexed Asset Library

**Date:** 2026-06-11
**Status:** Approved (design review with Jens)
**Goal:** Fix the generator's biggest quality gap — weak/missing imagery — by (1) growing the asset library from SharePoint with a curated import flow, (2) enriching every asset with vision-derived placement metadata, and (3) making the generator use that metadata so images land correctly and FIG placeholders never survive into final output.

## Problem

The generated decks' biggest visual weakness is imagery:

- `assets/library.json` holds only 13 assets, nearly all Kitchen Station / purifier packshots.
- Matching is shallow: tags compared to slide context, with no knowledge of what the image looks like, its aspect ratio, or whether it suits a full-bleed hero vs a small card.
- When nothing matches, FIG placeholders survive into the final deck.
- The full Bluewater image pool lives in SharePoint (MS365 MCP connected), unreachable by the pipeline today.

## Decision: import, don't fetch live

SharePoint is a **source to import from**, not a live dependency of `/generate-presentation`:

1. The generator places images by copying fills from Figma nodes — a SharePoint image must be uploaded into Figma (`upload_assets`) before it can land on a slide anyway.
2. SharePoint is unvetted (low-res, outdated, wrong-format files). A human keep/skip pass at import time keeps the library trustworthy; generation stays fast, deterministic, and offline from MS365 auth.

## Part 1 — Asset library v2 (`assets/library.json`)

Each asset gains a `visual` block (vision-written, from a screenshot of the Figma node) and a `source` block:

```json
"spirit-purifier-kitchen-lifestyle": {
  "nodeId": "61219:18000",
  "tags": ["lifestyle", "purifier", "spirit", "kitchen"],
  "description": "Spirit purifier installed under a bright Scandinavian kitchen sink, daylight, person filling a glass",
  "source": { "type": "sharepoint", "path": "Brand/2026/Lifestyle/spirit-kitchen.jpg", "importedAt": "2026-06-11" },
  "visual": {
    "aspect": 1.5,
    "orientation": "landscape",
    "tone": "light",
    "subject": "right",
    "suitability": ["hero", "full-bleed", "card"],
    "quality": "high"
  }
}
```

Field semantics:

- `aspect` — width/height measured from the Figma node (number, 2 decimals).
- `orientation` — `landscape | portrait | square` (derived from aspect; square = 0.9–1.1).
- `tone` — `light | dark | mixed`; drives text-overlay color on image-overlay templates.
- `subject` — `center | left | right | top | bottom`; where the visual subject sits, i.e. which zones are safe for text overlays.
- `suitability` — subset of `hero | full-bleed | card | detail | texture`; separates a full-bleed-worthy lifestyle shot from a small-card packshot.
- `quality` — `high | medium | low`; resolution sanity recorded at import. `full-bleed`/`hero` use requires `high`.
- `source` — provenance for dedupe on re-import. Existing assets indexed from Figma get `{ "type": "figma" }`.

**Backfill:** the 13 existing assets get the same treatment (screenshot node → write `visual` block).

**Validation gate:** new `tools/validate_assets.py`, mirroring `validate_products.py` / `validate_newsletters.py` (must end `OK`). Checks: required fields present, enums valid, `aspect` numeric and consistent with `orientation`, suitability non-empty, no duplicate `nodeId`, `source` present.

## Part 2 — `/import-assets` command (`.claude/commands/import-assets.md`)

```
/import-assets <search terms | folder path>
```

Flow:

1. **Search SharePoint** via the MS365 MCP (`sharepoint_search` / `sharepoint_folder_search`) for image files matching the terms.
2. **Curate:** present the candidate list (filename, path, size) to the user as keep/skip via AskUserQuestion. Dedupe against `library.json` `source.path` — already-imported files are listed as such, not re-offered.
3. **Fetch binaries** to a temp dir.
4. **Upload keepers** to the Figma "Brand Assets" page (`51124:14`) via the Figma MCP `upload_assets`, named with SEO-style asset keys (kebab-case, descriptive).
5. **Vision-index** each upload: screenshot the node, write `description`, `tags`, and the full `visual` block.
6. **Write `library.json`**, run `python3 tools/validate_assets.py` — must end `OK`.

**Spike first (gating step):** verify the MS365 MCP can deliver image **binaries**, not just metadata/links, end-to-end into Figma via `upload_assets` with one test image. **Fallback if it can't:** a locally synced OneDrive/SharePoint folder on the Mac, read directly from disk — steps 2–6 unchanged, `source.type: "onedrive-sync"`.

`/sync-assets` (Figma-side scan) remains for images that appear in Figma directly; it adopts the v2 schema and vision-indexing step.

## Part 3 — Generator upgrades (`generate-presentation.md` §5d rewrite)

1. **Two-stage matching.** Stage 1 semantic: rank assets by tags + description vs the slide's title/topic. Stage 2 geometric: filter by slot fit — slot aspect vs asset `aspect` (tolerance ±25%, or croppable when `subject` is `center`), full-bleed/hero slots require matching `suitability` and `quality: high`.
2. **Tone/subject-aware overlay.** On image-overlay templates (`full-bleed-hero`, `full-bleed-tech-hero`, covers): text color follows `tone` — `light` image → dark text variant, `dark`/`mixed` → light text variant (the existing template dark/light conventions, `isDark` in chrome); prefer assets whose `subject` keeps the title zone (bottom-left) clear; set fill `scaleMode: FILL`.
3. **No-placeholder gate.** If no asset passes both stages for a required image slot, do NOT ship the FIG placeholder: re-route the slide to the text-first equivalent template (e.g. `pillar-grid-4up-image` → `template-bento4`; full-bleed hero → `template-chapter-*`). Each re-route is reported in the Step 6 summary.
4. **Screenshot QA.** After the build, `get_screenshot` every slide that carries an image and check: real image present (no FIG placeholder), text legible over the image, no awkward crop (subject cut off). Fix what is fixable (swap asset, flip text tone); flag the rest in the summary. Complements `auditSlide` (geometry) with an imagery gate.

## Out of scope (YAGNI)

- Live SharePoint lookup during generation (rejected in design review).
- Generative imagery (Adobe/Firefly fill) when no asset matches — possible later layer, not now.
- Auto-cropping via `imageTransform` matrices — `scaleMode: FILL` + subject-aware asset choice covers the need; revisit only if QA keeps flagging crops.
- Newsletter renderer image upgrades — it already pulls hero images by `assetKey`; it benefits from the bigger library for free, no renderer change.

## Testing / verification

- `tools/validate_assets.py` green on the backfilled library before any import.
- Spike result documented in the command file (MCP binary fetch: works / fallback used).
- Regression: regenerate a sample deck (`samples/`) before/after the §5d rewrite; image slides must show real assets or documented re-routes — zero FIG placeholders in output.
- `tools/test_validate_assets.py` unit tests mirror the existing validator test pattern.

## Build order

1. Schema v2 + `validate_assets.py` + backfill the 13 existing assets.
2. Spike: SharePoint binary fetch → `upload_assets` round trip (one image).
3. `/import-assets` command (with whichever fetch path the spike proved).
4. §5d generator rewrite (matching, overlay, gate, QA).
5. Regression run on a sample deck + first real import batch.
