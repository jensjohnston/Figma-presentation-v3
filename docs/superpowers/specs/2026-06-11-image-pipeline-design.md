# Image Pipeline — SharePoint Import, Vision-Indexed Library + Curated Generation

**Date:** 2026-06-11
**Status:** Approved (design review with Jens; curation flow refined same day)
**Goal:** Fix the generator's biggest quality gap — weak/missing imagery — by (1) growing the asset library from SharePoint with a visual, curated import flow, (2) enriching every asset with vision-derived placement metadata, (3) making the generator use that metadata so images land correctly and FIG placeholders never survive, and (4) adding a curated generation mode where a human picks the layout and the images for each slide from rendered alternatives — with every pick logged so the generator's first guess keeps improving.

## Problem

The generated decks' biggest visual weakness is imagery:

- `assets/library.json` holds only 13 assets, nearly all Kitchen Station / purifier packshots.
- Matching is shallow: tags compared to slide context, with no knowledge of what the image looks like, its aspect ratio, or whether it suits a full-bleed hero vs a small card.
- When nothing matches, FIG placeholders survive into the final deck.
- The full Bluewater image pool lives in SharePoint (MS365 MCP connected), unreachable by the pipeline today.
- There is no human-in-the-loop review surface: the generator commits to one template and one image per slide, and fixing a wrong call means manual Figma work.

## Decision: import, don't fetch live

SharePoint is a **source to import from**, not a live dependency of `/generate-presentation`:

1. The generator places images by copying fills from Figma nodes — a SharePoint image must be uploaded into Figma (`upload_assets`) before it can land on a slide anyway.
2. SharePoint is unvetted (low-res, outdated, wrong-format files). A human keep/skip pass at import time keeps the library trustworthy; generation stays fast, deterministic, and offline from MS365 auth.

## Decision: curation happens in Figma, on rendered slides

Humans cannot judge images from filenames, paths, or sizes, and cannot judge layouts from template names. Every curation surface in this design is **visual and Figma-native**: real images in a grid, real slides rendered with real content. Figma is the tool the team already lives in; no browser galleries or extra tooling. Provenance (path/size) is recorded in `source` metadata for dedupe — never used as a decision surface.

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

1. **Search SharePoint** via the MS365 MCP (`sharepoint_search` / `sharepoint_folder_search`) for image files matching the terms. Dedupe against `library.json` `source.path` — already-imported files are skipped silently (listed in the report only).
2. **Fetch binaries** to a temp dir.
3. **Stage visually — the "Import inbox".** Upload ALL candidates to a staging grid section on the Brand Assets page (`51124:14`): labeled image cards (A1, A2, A3…) with the candidate filename as a small caption. The curator reviews real images in Figma (or via a screenshot of the grid in chat) and answers keep/skip per label ("keep A1, A3, B2").
4. **Index keepers:** rename to SEO-style asset keys (kebab-case, descriptive), move out of the inbox into the Brand Assets layout, vision-index each (screenshot → `description`, `tags`, full `visual` block). **Delete skips** from the inbox.
5. **Write `library.json`**, run `python3 tools/validate_assets.py` — must end `OK`.

**Spike first (gating step):** verify the MS365 MCP can deliver image **binaries**, not just metadata/links, end-to-end into Figma via `upload_assets` with one test image. **Fallback if it can't:** a locally synced OneDrive/SharePoint folder on the Mac, read directly from disk — steps 3–5 unchanged, `source.type: "onedrive-sync"`.

`/sync-assets` (Figma-side scan) remains for images that appear in Figma directly; it adopts the v2 schema and vision-indexing step.

## Part 3 — Generator image intelligence (`generate-presentation.md` §5d rewrite)

1. **Two-stage matching.** Stage 1 semantic: rank assets by tags + description vs the slide's title/topic. Stage 2 geometric: filter by slot fit — slot aspect vs asset `aspect` (tolerance ±25%, or croppable when `subject` is `center`), full-bleed/hero slots require matching `suitability` and `quality: high`. Preference boosts from `preferences.json` (Part 5) break ties.
2. **Tone/subject-aware overlay.** On image-overlay templates (`full-bleed-hero`, `full-bleed-tech-hero`, covers): text color follows `tone` — `light` image → dark text variant, `dark`/`mixed` → light text variant (the existing template dark/light conventions, `isDark` in chrome); prefer assets whose `subject` keeps the title zone (bottom-left) clear; set fill `scaleMode: FILL`.
3. **No-placeholder gate.** If no asset passes both stages for a required image slot, do NOT ship the FIG placeholder: re-route the slide to the text-first equivalent template (e.g. `pillar-grid-4up-image` → `template-bento4`; full-bleed hero → `template-chapter-*`). Each re-route is reported in the Step 6 summary.
4. **Screenshot QA.** After the build, `get_screenshot` every slide that carries an image and check: real image present (no FIG placeholder), text legible over the image, no awkward crop (subject cut off). Fix what is fixable (swap asset, flip text tone); flag the rest in the summary. Complements `auditSlide` (geometry) with an imagery gate.

## Part 4 — Curated generation: layout pass, then image pass

A new review stage inside `/generate-presentation`, replacing the text-only "Present the Slide Plan" confirmation for visual decisions. The curator always judges **finished, rendered slides** — real content, top-pick images applied — never template names or wireframes.

### Layout pass (adaptive alternatives)

- **Adaptive variant count:** slides whose content could plausibly go multiple ways get **3 rendered layout alternatives**; slides with one clear answer get **1** (covers, chapter dividers, closing, and product-pack clones — those are already-approved layouts). The matcher decides: if the top template choices score close together, it's ambiguous → 3 variants.
- **Review grid:** alternatives are built on the output page as a grid — one row per slide position, option **A** (the recommendation) first, **B**/**C** beside it, each labeled. All variants carry real content and their own top-pick images.
- **Picking:** the curator reviews in Figma and answers per slide ("4 → B", "rest A"). Chosen variants are assembled into the final deck row (standard positions, sequential naming, deck chrome); losing variants are deleted.

### Image pass (alternates strip)

- On each chosen slide that carries imagery, the top-pick image is already applied. A small **alternates strip** — 2–3 runner-up thumbnails labeled B, C, D — sits just below the slide, outside the deck row.
- The curator says "slide 4 → C" and the swap is applied instantly (copy fill from the alternate). When the curator confirms the deck, all strips are deleted and the deck is clean.

### Modes

Step 3 of `/generate-presentation` gains a third question: **Review mode** — `Curated` (layout pass + image pass, the default) or `Direct` (today's behavior: one shot, no review grid) for quick throwaway decks.

## Part 5 — Preference memory (`assets/preferences.json`)

Every curation decision is logged and fed back into ranking — the same self-improvement loop as `tasks/lessons.md`, structured:

```json
{
  "imagePicks": [
    { "context": { "role": "hero", "topic": "spirit purifier", "slot": "full-bleed" },
      "chosen": "spirit-purifier-kitchen-lifestyle",
      "rejected": ["bluewater-spirit-purifier-front"], "date": "2026-06-11" }
  ],
  "templatePicks": [
    { "context": { "contentShape": "4 items, image-rich", "deck": "beam-training" },
      "chosen": "pillar-grid-4up-image",
      "rejected": ["template-bento4", "bento-mix-center-hero"], "date": "2026-06-11" }
  ]
}
```

- **Write:** every layout pick, image pick, and image swap appends a record (confirming the default A counts as a pick too).
- **Read:** at matching time, both the template matcher and the image matcher use preference history as a **ranking tie-breaker** — an option repeatedly chosen for similar context gets boosted; one repeatedly swapped away gets demoted. Never overrides hard constraints (geometry, quality, suitability).
- This is a tie-breaker heuristic, not ML training. Effect: pick #1 is right more often, so curation rounds get shorter over time.

## Out of scope (YAGNI)

- Live SharePoint lookup during generation (rejected in design review).
- Generative imagery (Adobe/Firefly fill) when no asset matches — possible later layer, not now.
- Auto-cropping via `imageTransform` matrices — `scaleMode: FILL` + subject-aware asset choice covers the need; revisit only if QA keeps flagging crops.
- Newsletter renderer image upgrades — it already pulls hero images by `assetKey`; it benefits from the bigger library for free, no renderer change.
- Browser-based curation UI — Figma is the review surface; revisit only if in-Figma review proves clumsy in practice.
- ML-style training on preferences — the log is a ranking tie-breaker only.

## Testing / verification

- `tools/validate_assets.py` green on the backfilled library before any import.
- Spike result documented in the command file (MCP binary fetch: works / fallback used).
- Regression: regenerate a sample deck (`samples/`) before/after the §5d rewrite; image slides must show real assets or documented re-routes — zero FIG placeholders in output.
- Curated-mode dry run on a sample deck: layout grid renders, picks assemble correctly, strips clean up fully (no orphan variants/strips left on the page).
- `preferences.json` round trip: a pick recorded in one run measurably reorders the ranking in the next (verifiable in the slide-plan reasoning).
- `tools/test_validate_assets.py` unit tests mirror the existing validator test pattern.

## Build order

1. Schema v2 + `validate_assets.py` + backfill the 13 existing assets.
2. Spike: SharePoint binary fetch → `upload_assets` round trip (one image).
3. `/import-assets` command with the Import inbox flow (whichever fetch path the spike proved).
4. §5d generator rewrite (matching, overlay, gate, QA).
5. Curated generation mode (layout pass + image pass + cleanup) in `generate-presentation.md`.
6. Preference memory: log writes from curation, ranking reads in the matchers.
7. Regression run on a sample deck + first real import batch.
