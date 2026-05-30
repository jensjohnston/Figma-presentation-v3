# Product Content Library — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the generator product-aware — when a deck mentions a known product, it reuses the team's finished product slides (clone + rewrite text), pulls verified content, and places specific product images — driven by a new `products/registry.json` built from two existing Figma product pages.

**Architecture:** Additive layer over today's pipeline. Two finished product decks already exist as dedicated Figma pages ("Kitchen Station 1" `61219:17724`, 8 slides; "All purifiers" `61219:14889`, 9 slides). We (1) give their layers semantic names following the existing convention, (2) index their images into `assets/library.json`, (3) capture them in `products/registry.json` (role + matchHints + slots + image refs), (4) add a Claude-driven `/index-product` command that regenerates a product entry from Figma, and (5) wire product detection + product-first matching into `generate-presentation.md`. A Python validator (`tools/validate_products.py`) is the regression gate. The from-scratch path is untouched and remains the fallback.

**Tech Stack:** JSON registries (no build step — "Claude is the engine"), Figma Plugin API via `use_figma` MCP (always preceded by the `figma-use` skill) for reads/renames, Python 3 stdlib for validation, Markdown slash-command + design docs.

**Source spec:** `docs/superpowers/specs/2026-05-30-product-content-library-design.md`

**Canonical node IDs (verified via get_metadata 2026-05-30):**

Kitchen Station page `61219:17724`, slides left→right:
| x | frame nodeId | content | proposed frame name | registry role |
|---|---|---|---|---|
| 0 | `61219:17725` | full-bleed render + title | `ks-cover` | hero |
| 2547 | `61219:17731` | eyebrow + title "turn any water source…" + 3 mineral-ring columns | `ks-how-it-works-3up` | how-it-works |
| 4681 | `61219:17868` | café bg + title + body statement | `ks-statement-cafe` | value-prop |
| 6815 | `61219:17771` | café bg + title only | `ks-section-cafe` | use-case |
| 8949 | `61219:17777` | title + 3 bottle cards (heading/body/image) | `ks-range-3up` | use-case |
| 11083 | `61219:17794` | title + app image + body (Bluewater App) | `ks-app-feature` | value-prop |
| 13111 | `61219:17798` | title + 4-up Bento (cell-heading-1/cell-body-1 + iPhone) | `ks-features-4up` | how-it-works |
| 15183 | `61219:17829` | eyebrow+title + ecosystem cards (Purifier/Bluewater O/Liquid Rock®/App/Control Box) | `ks-ecosystem` | use-case |

All purifiers page `61219:14889`, slides left→right:
| x | frame nodeId | content | proposed frame name | registry role |
|---|---|---|---|---|
| 0 | `61219:17965` | cover image + title + logo | `purifier-cover` | hero |
| 2060 | `61219:17971` | filtration spectrum "Every filter has a limit" + body | `purifier-filtration-spectrum` | how-it-works |
| 4154 | `61219:18156` | "Engineered for Purity" 99.7% + Technology + mini-stats | `purifier-tech-superiorosmosis` | value-prop |
| 6248 | `61219:18130` | title + 3-up Bento + cert logos | `purifier-certifications-3up` | sustainability |
| 8388 | `61219:18007` | Cleone profile, 50% recovery, reverse-osmosis method | `purifier-profile-cleone` | use-case |
| 10409 | `61219:18042` | Spirit profile, 70% | `purifier-profile-spirit` | use-case |
| 12369 | `61219:18086` | Pro profile, 80% | `purifier-profile-pro` | use-case |
| 14601 | `61219:17997` | "Which Bluewater purifier is right for you?" + renders | `purifier-lineup` | comparison |
| 16716 | `61219:17872` | full spec comparison table (Header/Row/C0–C3) | `purifier-comparison-table` | comparison |

Stale duplicate purifier frames on **Template references** page `56881:463` (to be moved to a review page): `61219:14384, 61219:14477, 61219:14483, 61219:14509, 61219:14570, 61219:14605, 61219:14649, 61219:14712, 61219:14738`.

---

## Naming Convention (applies to all naming tasks)

Follow the **existing** convention from `templates/registry.json` + `design-system.md`. Do NOT invent new vocabulary.

**Keep as-is** (already semantic): `title`, `body`, `heading`, `caption`, `cell-heading-N`, `cell-body-N`, `bullet-heading-N`, `bullet-body-N`, `meta-left`, `meta-right`, `meta-top-right`.

**Rename content-named text nodes** to slot roles:
- Product name text (e.g. node named `"Cleone"`, `"Spirit"`, `"Pro"`) → `product-name`
- Product tagline/descriptor (e.g. `"Powerful yet compact…"`) → `product-desc`
- Big stat number (e.g. `"50%"`, `"99.7%"`) → `stat-value`
- Stat prefix (e.g. `"Up to"`) → `stat-prefix`
- Stat caption (e.g. `"Water recovery. Conventional RO reaches ~25%."`) → `stat-label`
- Method/section label (e.g. `"Purification method"`, `"Technology"`, `"Engineered for Purity"`) → `eyebrow` (it is the small label above a block)
- Method name (e.g. `"Reverse osmosis"`, `"SuperiorOsmosis™"` used as a heading) → `heading`
- Method/body prose → `body`
- A trailing 19–20px split-glyph node also named `"title"` (the period/widow-fix shard) → `title-end`
- Comparison-table cells: column headers → `col-heading-N` (N=1..3, left→right product columns; the empty C0 header stays `​`/`row-label-header`), row label (C0 cell) → `row-label-N`, data cells → `cell-N-C` where N=row index, C=column index (1–3). Keep the existing `Header`/`Row`/`C0..C3`/`Div` container frame names — they are already clean.

**Leave untouched** (generator never targets these): decorative shapes/groups — `Ellipse N`, `Line N`, `Vector`, `Group N`, `Frame NNNN`, `Clip path group`, `clip0`, ring-graphic `Frame 1002/761/762/1003`, and image-bearing `rounded-rectangle` nodes whose names are render filenames (those are handled by the image-index task, not renamed here).

**Frame (slide) names**: rename each slide frame to the unique name in the tables above. Leave inner structural frames alone unless explicitly listed.

**Slot-text capture:** during each naming task, after reading the slide, append the actual slot text to scratch file `tasks/product-index-scratch.json` under the slide's frame nodeId (used later to build the registry without re-reading every slide). This file is gitignored scratch (see `.gitignore` `tasks/` rule).

---

## Phase 0 — Archive duplicate purifier slides

### Task 1: Move stale purifier frames off the Template references page

**Files:** Figma only (no repo files).

- [ ] **Step 1: Load the figma-use skill**

Invoke the `figma-use` skill (MANDATORY before any `use_figma` call).

- [ ] **Step 2: Create a review page and move the 9 stale frames**

Run via `use_figma` (file `GkUiwJTK5Xi65AKw4MOjTL`):

```js
const ids = ["61219:14384","61219:14477","61219:14483","61219:14509","61219:14570","61219:14605","61219:14649","61219:14712","61219:14738"];
const page = figma.createPage();
page.name = "Archive — old purifiers (review)";
let moved = [];
for (const id of ids) {
  const n = await figma.getNodeByIdAsync(id);
  if (n) { page.appendChild(n); moved.push(id); }
}
return { movedCount: moved.length, moved, pageId: page.id };
```

Expected: `movedCount: 9`.

- [ ] **Step 3: Verify removal from the template page**

Run `get_metadata` on `56881:463`; confirm none of the 9 IDs remain as children (re-run the page-children parse from the session, or grep the saved dump). Expected: 0 of the 9 present on `56881:463`; all 9 present under the new page.

- [ ] **Step 4: Commit (doc note only — Figma has no git)**

No repo change yet; record the new review-page id in the plan's runtime notes for Task 9 (registry must NOT reference it).

---

## Phase 1 — Semantic layer naming (17 slides)

Each task below is one slide: read it, rename its frame + content-named text nodes per the Convention, capture slot text to scratch, verify. Every task starts assuming the `figma-use` skill is already loaded (from Task 1); reload it if starting a fresh session.

**Per-slide procedure (identical for every Phase-1 task):**
1. `get_design_context` (or `get_metadata` + `get_screenshot`) for the frame to read exact text per node.
2. Build a rename map `{nodeId: newName}` applying the Convention. Only include content-named text nodes + the frame itself.
3. Apply with one `use_figma` batch:
   ```js
   const renames = { /* nodeId: "newName", ... */ };
   const out = [];
   for (const [id, name] of Object.entries(renames)) {
     const n = await figma.getNodeByIdAsync(id);
     if (n) { n.name = name; out.push(id); }
   }
   return { renamed: out.length };
   ```
4. Append slot text to `tasks/product-index-scratch.json`: `{ "<frameId>": { "frameName": "...", "role": "...", "slots": { "title": "actual text", ... } } }`.
5. Verify: re-read the frame's metadata; assert (a) frame name == target, (b) no remaining text node whose name equals its own text content (i.e. no content-named text nodes left). Expected: pass.

### Task 2: `ks-cover` (`61219:17725`)
Known renames: frame → `ks-cover`; `61219:17729` keep `title`; `61219:17730` (19px shard) → `title-end`. Image `61219:17726`/`61219:17727` left for image-index task.

### Task 3: `ks-how-it-works-3up` (`61219:17731`)
Frame → `ks-how-it-works-3up`. Eyebrow above title: `61219:17767` ("We turn any water source…") is the body/eyebrow — name `eyebrow`. Title shards `61219:17769/17770` → `title` / `title-end`. The three columns each have `H3 Medium` + `Body`: rename `H3 Medium`→`cell-heading-1/2/3` (by x order: 17735, 17757, 17763) and `Body`→`cell-body-1/2/3` (17736, 17758, 17764). Container frames `Text block`, `Frame 1192/1193/1195`, mineral-ring `Frame`/`Group`/`Vector` left untouched.

### Task 4: `ks-statement-cafe` (`61219:17868`)
Frame → `ks-statement-cafe`. `61219:17871` `title` keep; `61219:17870` `body` keep. Café image left for image-index.

### Task 5: `ks-section-cafe` (`61219:17771`)
Frame → `ks-section-cafe`. Title shards `61219:17775/17776` → `title`/`title-end`. Images left.

### Task 6: `ks-range-3up` (`61219:17777`)
Frame → `ks-range-3up`. Three `card-bottle-1` cards each `heading`+`body` (keep names; they're semantic). Number them for clarity: card1 (17779/17780)→`cell-heading-1`/`cell-body-1`, card2 (17783/17784)→`-2`, card3 (17787/17788)→`-3`. Title shards `17791/17792` → `title`/`title-end`; `61219:17793` `title` keep (it is the second-line title) — rename to `title-2`. Product images (`Pro - Front 1`) left for image-index.

### Task 7: `ks-app-feature` (`61219:17794`)
Frame → `ks-app-feature`. `61219:17795` `title` keep; `61219:17797` (long app copy) → `body`. App image `61219:17796` left.

### Task 8: `ks-features-4up` (`61219:17798`)
Frame → `ks-features-4up`. `61219:17799` `title` keep. Four Bento-3 cells each `cell-heading-1`/`cell-body-1` — renumber to `cell-heading-1..4` / `cell-body-1..4` by x order: (17804/17805)=1, (17811/17812)=2, (17818/17819)=3, (17825/17826)=4. iPhone images left.

### Task 9: `ks-ecosystem` (`61219:17829`)
Frame → `ks-ecosystem`. Eyebrow+title shards `17865/17866`→`title`/`title-end`; `61219:17867` `title`→`title-2`. Ecosystem cards each have `heading`+`body` (+ one `caption` 17854) — keep those semantic names but number per card by x then y: hero-card `Purifier` (frame `hero-card · Purifier`) has no text. Cards: `card · Bluewater O` (17835/17836)→`cell-heading-1`/`cell-body-1`; `card · Liquid Rock®` (17842/17843)→`-2`; `card · Bluewater O` #2 (17847/17848)→`-3`; `card · Liquid Rock®` #2 (17852/17853/caption 17854)→`-4` (+`cell-caption-4`); `card · Bluewater App` (17857/17858)→`-5`; `card · Control Box` (17862/17863)→`-6`. Keep the `card · …` container frame names (they label the ecosystem items — useful). Product images left.

### Task 10: `purifier-cover` (`61219:17965`)
Frame → `purifier-cover`. `61219:17970` `title` keep; `meta-top-right` `61219:17967` keep. Logo `Icons/Light/Left/Logo` + image left.

### Task 11: `purifier-filtration-spectrum` (`61219:17971`)
Frame → `purifier-filtration-spectrum`. `61219:17993` ("Every filter has a limit.") → `title`; `61219:17994` `body` keep; `61219:17973` (electrolytes copy, off-canvas) → `body-2`. The spectrum band labels (`Particle filtration`, `Microfiltration`, … `Reverse osmosis`) and micron specs are a labeled diagram → name labels `spectrum-label-1..6` and micron specs `spectrum-spec-1..6` (left→right by x: 17974/17975, 17977/17978, 17980/17981, 17983/17984, 17989/17990, 17986/17987). `meta-left/right` keep. Lines/vectors left.

### Task 12: `purifier-tech-superiorosmosis` (`61219:18156`)
Frame → `purifier-tech-superiorosmosis`. `Engineered for Purity` (18158) → `eyebrow`; `99.7%` (18159) → `stat-value`; contaminants copy (18160) → `stat-label`. `Technology` (18180) → `eyebrow-2`; `SuperiorOsmosis` (18182) → `heading`; world's-most-efficient copy (18183) → `body`; `™` (18184) → `heading-trademark`. Mini-stat cards each `heading`+`body` (18187/18188, 18190/18191, 18193/18194) → keep `heading`/`body` but number `cell-heading-1..3`/`cell-body-1..3`. Ring graphics + hidden `Frame 1002` left.

### Task 13: `purifier-certifications-3up` (`61219:18130`)
Frame → `purifier-certifications-3up`. `61219:18150` `title` keep. Three empty Bento-3 cells (18132/18138/18144) left. Cert/logo images (`image 10/11/12`) left for image-index. `meta-left/right` keep.

### Task 14: `purifier-profile-cleone` (`61219:18007`)
Frame → `purifier-profile-cleone`. `Cleone` (18019) → `product-name`; smart-choice desc (18021) → `product-desc`. Stat block: `Up to`(18009)→`stat-prefix`, `50%`(18010)→`stat-value`, recovery caption(18011)→`stat-label`. Method block: `Purification method`(18035)→`eyebrow`, `Reverse osmosis`(18033)→`heading`, removes-99% copy(18034)→`body`. `meta-left/right` keep. Ring graphic (hidden `Frame 1002`), product renders, `Osmosis _Zoom_thumb`, `image 11` left.

### Task 15: `purifier-profile-spirit` (`61219:18042`)
Frame → `purifier-profile-spirit`. `Spirit`(18048)→`product-name`; desc(18050)→`product-desc`. `SuperiorOsmosis™`(18063)→`heading`; goes-beyond copy(18064)→`body`; `Purification method`(18065)→`eyebrow`. Stat: `Up to`(18081)→`stat-prefix`, `70%`(18082)→`stat-value`, caption(18083)→`stat-label`. `meta-left/right` keep. Rings/renders left.

### Task 16: `purifier-profile-pro` (`61219:18086`)
Frame → `purifier-profile-pro`. `Pro`(18092)→`product-name`; made-in-Sweden desc(18094)→`product-desc`. `SuperiorOsmosis™`(18107)→`heading`; goes-beyond copy(18108)→`body`; `Purification method`(18109)→`eyebrow`. Stat: `Up to`(18125)→`stat-prefix`, `80%`(18126)→`stat-value`, caption(18127)→`stat-label`. `meta-left/right` keep.

### Task 17: `purifier-lineup` (`61219:17997`)
Frame → `purifier-lineup`. `Which Bluewater purifier is right for you?`(18005)→`title`. `meta-left/right` keep. Product renders left.

### Task 18: `purifier-comparison-table` (`61219:17872`)
Frame → `purifier-comparison-table`. Container frames `Specs Table`/`Header`/`Row`/`C0..C3`/`Div` keep. Column headers: `Cleone`(17878)→`col-heading-1`, `Spirit`(17880)→`col-heading-2`, `Pro`(17882)→`col-heading-3`; empty header (17876) → `row-label-header`. Row labels (C0 cells): `Installation (W×D×H)`(17886)→`row-label-1`, `Water purification rate`(17896)→`row-label-2`, `Recovery rate`(17906)→`row-label-3`, `Flow per day`(17916)→`row-label-4`, `Purification technology`(17926)→`row-label-5`, `Best for`(17936)→`row-label-6`, `Included`(17946)→`row-label-7`, `Certifications`(17956)→`row-label-8`. Data cells `cell-<row>-<col>`: row1 (17888/17890/17892)=`cell-1-1/1-2/1-3`; row2 (17898/17900/17902); row3 (17908/17910/17912); row4 (17918/17920/17922); row5 (17928/17930/17932); row6 (17938/17940/17942); row7 (17948/17950/17952); row8 (17958/17960/17962). `meta-left/right` keep.

- [ ] **Phase 1 verification (after Tasks 2–18):** Run a scan over fresh `get_metadata` of both pages confirming: every slide frame has its unique target name; no text node's `name` equals its own rendered text (no content-named text nodes remain); `tasks/product-index-scratch.json` has an entry for all 17 frames. Commit any repo artifacts (scratch is gitignored).

---

## Phase 2 — Image index

### Task 19: Inventory product images and add them to `assets/library.json`

**Files:** Modify `assets/library.json`.

- [ ] **Step 1: Collect image-bearing nodes**

From the captured metadata, list every `rounded-rectangle`/image node under the 17 slides whose name is a render filename (e.g. `KS1_Palma_Stills_3.1.1`, `Cleone - Side 1`, `Spirit - Front 4`, `Pro - Front 1`, `Osmosis _Zoom_thumb 1`, `iPhone 16e`, `image 10/11/12`, café `Coffee_Gemini…`, `image (3) 1`, `Bottle_with pump bubble 4`, `Pump_Front 1`). Deduplicate by visual subject.

- [ ] **Step 2: Add asset entries with SEO-friendly keys**

For each unique image add to `assets/library.json` `assets` map, following the existing schema (`nodeId`, `tags`, `description`) and the SEO image-naming rule (lowercase, hyphen-separated, brand keywords). Example:

```json
"kitchen-station-palma-hero": {
  "nodeId": "61219:17726",
  "tags": ["product", "kitchen-station", "hero"],
  "description": "Kitchen Station Palma lifestyle render — countertop hero"
},
"purifier-cleone-side": {
  "nodeId": "61219:18017",
  "tags": ["product", "purifier", "cleone"],
  "description": "Cleone purifier, side view"
}
```

- [ ] **Step 3: Validate JSON**

Run: `python3 -c "import json;json.load(open('assets/library.json'));print('ok')"`
Expected: `ok`.

- [ ] **Step 4: Commit**

```bash
git add assets/library.json
git commit -m "feat(assets): index Kitchen Station + purifier product images"
```

---

## Phase 3 — Product registry + validator

### Task 20: Write the registry validator (the regression gate)

**Files:** Create `tools/validate_products.py`.

- [ ] **Step 1: Write the validator**

```python
#!/usr/bin/env python3
"""Validate products/registry.json against the product-pack contract."""
import json, sys, pathlib

ROLES = {"hero","key-specs","how-it-works","value-prop","comparison",
         "pricing","sustainability","use-case","cta"}

def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    reg = json.load(open(root/"products"/"registry.json"))
    lib = json.load(open(root/"assets"/"library.json"))
    asset_keys = set(lib.get("assets", {}))
    errors = []
    products = reg.get("products", {})
    if not products:
        errors.append("no products defined")
    for slug, p in products.items():
        for field in ("displayName","pageId","aliases","slides"):
            if field not in p:
                errors.append(f"{slug}: missing '{field}'")
        if not isinstance(p.get("aliases"), list) or not p.get("aliases"):
            errors.append(f"{slug}: aliases must be a non-empty list")
        seen_nodes = set()
        for i, s in enumerate(p.get("slides", [])):
            for field in ("role","nodeId","matchHints","slots"):
                if field not in s:
                    errors.append(f"{slug}.slides[{i}]: missing '{field}'")
            if s.get("role") not in ROLES:
                errors.append(f"{slug}.slides[{i}]: bad role {s.get('role')!r}")
            if s.get("nodeId") in seen_nodes:
                errors.append(f"{slug}.slides[{i}]: duplicate nodeId {s.get('nodeId')}")
            seen_nodes.add(s.get("nodeId"))
        for j, img in enumerate(p.get("images", [])):
            key = img.get("assetKey")
            if key not in asset_keys:
                errors.append(f"{slug}.images[{j}]: assetKey {key!r} not in assets/library.json")
    if errors:
        print("FAIL")
        for e in errors: print(" -", e)
        sys.exit(1)
    print(f"OK — {len(products)} products, "
          f"{sum(len(p.get('slides',[])) for p in products.values())} slides")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it — expect failure (no registry yet)**

Run: `python3 tools/validate_products.py`
Expected: FAIL or FileNotFoundError on `products/registry.json` (proves the gate works before the registry exists).

- [ ] **Step 3: Commit**

```bash
git add tools/validate_products.py
git commit -m "test(products): add product registry validator"
```

### Task 21: Build `products/registry.json` from the scratch capture

**Files:** Create `products/registry.json`.

- [ ] **Step 1: Assemble the registry**

Consume `tasks/product-index-scratch.json` (slot text captured in Phase 1) + the role assignments from the frame tables + image `assetKey`s from Task 19. Shape (mirrors `templates/registry.json` top-level):

```json
{
  "fileKey": "GkUiwJTK5Xi65AKw4MOjTL",
  "products": {
    "kitchen-station": {
      "displayName": "Kitchen Station",
      "pageId": "61219:17724",
      "aliases": ["kitchen station","kitchen-station","kitchenstation","kitchen"],
      "slides": [
        { "role": "hero", "nodeId": "61219:17725", "frameName": "ks-cover",
          "matchHints": "Product cover / opening slide for Kitchen Station — full-bleed lifestyle render + product title.",
          "slots": { "title": "<captured>", "title-end": "<captured>" } }
        /* …one entry per KS slide, role per frame table… */
      ],
      "content": { "valueProps": ["<captured>"], "keySpecs": ["<captured>"] },
      "images": [ { "assetKey": "kitchen-station-palma-hero" } ]
    },
    "purifiers": {
      "displayName": "All purifiers",
      "pageId": "61219:14889",
      "aliases": ["purifier","purifiers","water purifier","cleone","spirit","pro","superiorosmosis","reverse osmosis"],
      "slides": [
        { "role": "comparison", "nodeId": "61219:17872", "frameName": "purifier-comparison-table",
          "matchHints": "Side-by-side spec comparison of Cleone vs Spirit vs Pro across install size, purification rate, recovery, flow, technology, best-for, included, certifications.",
          "slots": { "col-heading-1": "Cleone", "col-heading-2": "Spirit", "col-heading-3": "Pro" } }
        /* …one entry per purifier slide… */
      ],
      "content": {
        "keySpecs": ["Cleone: 99% / 50% recovery / up to 610 L/day", "Spirit: 99.7% / 70% / up to 3,800 L/day", "Pro: 99.7% / 80% / up to 7,600 L/day"],
        "valueProps": ["SuperiorOsmosis removes up to 99.7% of contaminants", "Up to 80% water recovery vs ~25% conventional RO"]
      },
      "images": [ { "assetKey": "purifier-cleone-side" }, { "assetKey": "purifier-spirit-front" }, { "assetKey": "purifier-pro-front" } ]
    }
  }
}
```

Fill every `<captured>` from scratch — no placeholders in the committed file. Include all 8 KS + 9 purifier slides.

- [ ] **Step 2: Validate**

Run: `python3 tools/validate_products.py`
Expected: `OK — 2 products, 17 slides`.

- [ ] **Step 3: Commit**

```bash
git add products/registry.json
git commit -m "feat(products): add product registry for Kitchen Station + purifiers"
```

---

## Phase 4 — `/index-product` command

### Task 22: Author the `/index-product` slash command

**Files:** Create `.claude/commands/index-product.md`.

- [ ] **Step 1: Write the command**

A Claude-driven command, argument = product slug or Figma page URL. It must instruct Claude to:
1. Resolve the product page (slug → `pageId` from `products/registry.json`, or parse a pasted Figma node URL).
2. `get_metadata` the page; for each slide frame `get_design_context` to read text.
3. Apply the **Naming Convention** section of this plan's design (reference `docs/superpowers/specs/2026-05-30-product-content-library-design.md`) — propose frame name + slot renames, show the user the map, apply via `figma-use` + `use_figma` after confirmation.
4. Add images to `assets/library.json` (SEO names) and propose `role` + `matchHints` per slide (user confirms).
5. Write/replace the product entry in `products/registry.json`.
6. Run `python3 tools/validate_products.py` and report the result. Must end green.

Include the role vocabulary and the keep/rename/leave rules verbatim so the command is self-contained.

- [ ] **Step 2: Verify presence**

Run: `test -f .claude/commands/index-product.md && grep -c "validate_products" .claude/commands/index-product.md`
Expected: file exists, count ≥ 1.

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/index-product.md
git commit -m "feat: add /index-product command"
```

---

## Phase 5 — Generator integration + docs

### Task 23: Wire product detection + product-first matching into `generate-presentation.md`

**Files:** Modify `.claude/commands/generate-presentation.md`.

- [ ] **Step 1: Read the current pipeline section**

Identify the numbered pipeline steps (read PDF → extract → read registries → match template → generate).

- [ ] **Step 2: Insert the product steps**

Add, without altering the existing from-scratch fallback:
- After "extract content": **"Detect products — load `products/registry.json`; scan the deck's full text against every product's `aliases`; record matched product slugs."**
- After "read templates/registry.json": **"If any product matched, load its product pack (slides + content + images)."**
- In the per-slide matching step: **"Product-first: if a matched product has a slide whose `role` + `matchHints` fit this slide's intent, CLONE that product slide and rewrite its text slots from the incoming PDF (decision 5a — always rewrite; fall back to the product `content` block when the PDF is thin), then place referenced product images. Only if no product slide fits, build from scratch with generic templates (today's behavior), still preferring product `content` + images when filling."**

Keep the slideContract / audit gate applied to product clones too.

- [ ] **Step 3: Verify**

Run: `grep -c "products/registry.json\|Product-first\|aliases" .claude/commands/generate-presentation.md`
Expected: ≥ 3.

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/generate-presentation.md
git commit -m "feat: product-first matching in generate-presentation"
```

### Task 24: Document the product layer in CLAUDE.md

**Files:** Modify `CLAUDE.md`.

- [ ] **Step 1: Add a "Product Content Library" subsection**

Under Architecture/Design System: describe `products/registry.json` (product packs: slides role+matchHints+slots, content, image refs into `assets/library.json`), the product-first rule, and `/index-product` for authoring. Add a one-line "Adding a New Product" pointer mirroring "Adding New Templates".

- [ ] **Step 2: Verify**

Run: `grep -c "products/registry.json\|index-product" CLAUDE.md`
Expected: ≥ 2.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: document product content library + /index-product"
```

### Task 25: End-to-end smoke check

- [ ] **Step 1: Re-run the validator**

Run: `python3 tools/validate_products.py`
Expected: `OK — 2 products, 17 slides`.

- [ ] **Step 2: Dry-run the detection logic on a sample**

Reason through a one-line "deck mentions Kitchen Station and the purifier lineup" prompt against the `aliases` in `products/registry.json`; confirm both products would be detected and that `purifier-comparison-table` would be the product-first pick for a "compare the models" slide. Record the trace in the plan's review section. (No Figma generation required for this gate.)

- [ ] **Step 3: Final commit (if any doc/scratch artifacts changed)**

```bash
git add -A && git commit -m "chore: product content library increment complete"
```

---

## Self-Review (filled at plan-write time)

**Spec coverage:** Data model → Tasks 20–21. Per-product page org → already true (Phase 0 confirms single source). Product-first → Task 23. Role+matchHints → Tasks 18/21 + validator role check. Images referenced from asset library → Tasks 19/21 + validator `assetKey` check. Always-rewrite (5a) → Task 23 wording. `/index-product` → Task 22. Role vocabulary → enforced in `tools/validate_products.py`. CLAUDE.md docs → Task 24. All spec sections map to a task.

**Placeholder scan:** The only `<captured>`/`/* … */` markers are in Task 21's *illustrative* registry skeleton; Step 1 explicitly requires filling every one from scratch and Step 2's validator fails on a malformed/empty registry — so no placeholder can survive into the committed artifact.

**Type/name consistency:** Slot vocabulary, role set, and node IDs are used identically across naming tasks, the validator (`ROLES`), and the registry. Frame names in the tables match those referenced in Tasks 2–18 and the registry `frameName` fields.

**Scope:** One cohesive feature delivered in 5 phases with commit checkpoints; Phase boundaries (0→1→2→3→4→5) are natural review gates if you prefer to pause between them.
