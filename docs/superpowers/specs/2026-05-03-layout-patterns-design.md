# Layout Patterns + Chrome Compliance — Design

**Date:** 2026-05-03
**Status:** Approved (awaiting user review of written spec)
**Reference Figma page:** `Pattern Preview — 2026-05-03` (id `57300:2`) in Bluewater 2026 file

## Why

The presentation generator over-relies on text-only templates (bullets, info, list-row, table) when content would land better as a bento, full-bleed image, or pentagrid. Three concrete problems show up in generated decks:

1. **Generic visuals** — bullets and info-lefts dominate even when the source PDF has stat-heavy or image-friendly content.
2. **Divider lines mid-grid** — the List Row pattern's 1px Gray/200 divider gets rendered inside layouts that visually read as "a grid," not "a list."
3. **Chrome drift** — slide-level meta and title positions can land at (0,0) instead of (48,48) and (48,115). Prose-only rules in `design-system.md` are a brittle source of truth.

## Goals

- Bento + full-bleed images become the **default vocabulary**. Tables stay first-class for data. Bullets/info templates are last-resort fallbacks.
- Five new layout patterns derived from the user's reference designs (file `GkUiwJTK5Xi65AKw4MOjTL`, page `Template references` id `56881:463`) become first-class buildable patterns.
- Chrome positioning becomes **mechanically enforced** — a single helper writes meta/meta-right/title at exact anchors, an audit catches drift before any slide ships.
- The divider rule becomes explicit: dividers belong only in the List Row pattern.
- Image slots that have no matching asset render as **FIG placeholders** (option B in user's choice), so missing imagery is obvious and replaceable.

## Non-goals

- Overhauling existing templates. The 41 templates in `registry.json` stay. Patterns are additive.
- Animations, motion, or interactive prototypes. Slides are static.
- Auto-syncing real imagery. Asset library workflow is unchanged; FIG placeholders fill any gap.
- PowerPoint export. Phase 2.

## The systemic fix — four pillars

### 1. Single source of truth for chrome anchors

Add a top-level `chrome` block to `templates/registry.json`:

```json
"chrome": {
  "metaLeft":  { "x": 48, "y": 48 },
  "metaRight": { "rightX": 1872, "y": 48 },
  "title":     { "x": 48, "y": 115, "size": 64, "weight": "Semi Bold", "lh": 110, "color": "#18181B", "maxRows": 2 },
  "metaTypography": { "size": 14, "weight": "Regular", "lh": 134 },
  "metaColorOnLight": "#71717A",
  "metaColorOnDark":  "#A1A1AA",
  "titleColorOnLight": "#18181B",
  "titleColorOnDark":  "#FFFFFF",
  "contentTopY": 287,
  "lastElementBottomY": 1032,
  "horizontalMargin": 48,
  "topMargin": 48,
  "bottomMargin": 48
}
```

Every pattern script reads these numbers — no hardcoded literals in build code.

### 2. `applyChrome()` — the only sanctioned way to place chrome

Add to `templates/design-system.md`'s "Canonical text helper" section:

```js
function applyChrome(slide, opts) {
  const { metaLeftText, metaRightText, titleText, titleWidth = 1824, isDark = false } = opts;
  const C = REGISTRY.chrome; // load from registry.json
  const grayMeta  = isDark ? C.metaColorOnDark  : C.metaColorOnLight;
  const titleClr  = isDark ? C.titleColorOnDark : C.titleColorOnLight;

  const meta = mkText(slide, metaLeftText, {
    size: C.metaTypography.size, style: C.metaTypography.weight, color: hex(grayMeta),
    x: C.metaLeft.x, y: C.metaLeft.y, name: "meta",
  });

  let metaR = null;
  if (metaRightText) {
    metaR = mkText(slide, metaRightText, {
      size: C.metaTypography.size, style: C.metaTypography.weight, color: hex(grayMeta),
      name: "meta-right",
    });
    metaR.x = C.metaRight.rightX - metaR.width;
    metaR.y = C.metaRight.y;
  }

  let title = null;
  if (titleText) {
    title = mkText(slide, titleText, {
      size: C.title.size, style: C.title.weight, color: hex(titleClr),
      lh: C.title.lh, width: titleWidth, x: C.title.x, y: C.title.y, name: "title",
    });
  }
  return { meta, metaR, title };
}
```

Pattern build scripts may not hand-position chrome elements. The helper is the only path.

### 3. `auditChrome()` — validator that runs at the end of every slide

```js
function auditChrome(slide) {
  const C = REGISTRY.chrome;
  const issues = [];
  const m  = slide.children.find(n => n.type === "TEXT" && n.name === "meta");
  const mR = slide.children.find(n => n.type === "TEXT" && n.name === "meta-right");
  const tt = slide.children.find(n => n.type === "TEXT" && n.name === "title");

  if (m && (m.x !== C.metaLeft.x || m.y !== C.metaLeft.y))
    issues.push({ node: "meta", at: [m.x, m.y] });

  if (mR && (Math.round(mR.x + mR.width) !== C.metaRight.rightX || mR.y !== C.metaRight.y))
    issues.push({ node: "meta-right", rightEdge: Math.round(mR.x + mR.width), y: mR.y });

  if (tt) {
    if (tt.x !== C.title.x || tt.y !== C.title.y)
      issues.push({ node: "title", at: [tt.x, tt.y] });
    const maxH = C.title.size * (C.title.lh / 100) * C.title.maxRows + 1;
    if (tt.height > maxH)
      issues.push({ node: "title", reason: "exceeds 2 rows", h: tt.height, maxAllowed: maxH });
  }
  return issues;
}
```

`generate-presentation.md` Step 5b becomes: build → audit → if issues, fix before next slide.

### 4. Patterns as runnable code

Each of the 5 patterns ships with a build function in `design-system.md` (in a code fence, similar to how `mkText` is documented today). The generator calls the function with content; the function does the layout. Geometry lives as code, not prose.

## The five layout patterns

### A. full-bleed-hero
**When:** chapter dividers, dramatic single-statement slides.
**Anatomy:** image fills 1920×1080. `applyChrome({ titleText: null, isDark: true })` writes meta + Fig label only — title is anchored bottom-left in a `title-block` auto-layout frame containing eyebrow (32 Medium 110%, Blue/400 on dark) + bottom-title (64 Semi Bold 110%, White, max 2 rows) + body (16 Medium 134%, White at 80% opacity). Block bottom edge = `lastElementBottomY` (1032).
**FIG fallback:** Gray/900 slide bg + dashed Gray/600 outline 16px from edges + corner radius 16.

### B. split-portrait
**When:** testimonials, "person/place" moments, before/after.
**Anatomy:** standard chrome (meta + meta-right + title at width 880). Body block on left at y=287, width 880, vertical auto-layout (label + body, 24px itemSpacing). Right card 896×984 from y=48 to y=1032, Gray/100 bg, 32px corners, FIG placeholder inside.
**Title cap:** title must fit **2 rows at width 880** in 64 Semi Bold 110% (`auditChrome` flags titles taller than `64 × 1.1 × 2 = 140.8px`). If the source title doesn't fit, shorten it OR move the long line into a `subtitle` node below.

### C. pentagrid
**When:** one dominant idea + 3 supporting points (most common product/feature shape).
**Anatomy:** standard chrome. Left column: 3 sm-compact cards 587×227 stacked at x=48, y=287/546/805 (32 gutters). Each = label/heading/body. Right hero: 1205×745 at x=667, y=287, dark bg, FIG dashed outline + impact stat block (label 24 Medium / heading 80 Semi Bold 110% / body 24 Medium) anchored bottom-left of hero card with 48px padding.
**Total content width:** 587 + 32 + 1205 = 1824 ✓

### D. image-pillar-grid
**When:** 2–4 distinct items of equal weight (product lineups, features, locations).
**Anatomy:** standard chrome. N equal columns. Each column = vertical auto-layout card 432×745 (4-up; 3-up uses 587). Image area at top (FILL horizontal, FIXED 356 vertical, tinted FIG fill at 8% opacity). Text block below (FILL both, 48 padding, label 24 Medium / heading 36 Semi Bold or 56 if impact / body 24 Medium).
**Color tints (when no asset):** Blue/Green/Rose/Blue token at 8% — gives visual rhythm without fake imagery.

### E. image-bento-mix
**When:** 4–6 items with a hero visual and mixed text/stat/image cards.
**Anatomy:** standard chrome. 3-column layout (587 + 32 + 587 + 32 + 587 = 1825). Center column = full-height FIG image card 587×745. Left and right columns = 2 sm-compact cards each (356 tall, 32 gutter between). Mix freely: text card (Gray/100 bg), color-block stat card (Blue/600 / Green/600 with white text), small FIG card.

## Matching priority rewrite — `generate-presentation.md` Step 4

New priority order, replacing the existing list (lines 88–113):

1. **First slide** → existing title templates.
2. **Single statement, dramatic visual moment** → `full-bleed-hero`.
3. **Single dramatic stat with optional explanation** → existing `template-huge-fact*` if no supporting points; `pentagrid` if 1 hero stat + 3 supporting points.
4. **Multiple metrics 2–4** — pick by dominance:
   - One metric is clearly dramatic (largest number, brand-defining stat) → `pentagrid` with that stat as the hero.
   - All metrics are roughly equal weight → `image-pillar-grid`.
   - 4 metrics with no clear hero → `image-pillar-grid` (4 columns).
5. **Quote with attribution** → existing quote templates.
6. **Side-by-side comparison or testimonial/portrait** → `split-portrait` or existing `template-comparison-50-50`.
7. **2–4 items of equal weight (products, features, pillars)** → `image-pillar-grid`.
8. **4–6 items, varied content with one hero visual** → `image-bento-mix`.
9. **Pricing / tiers** → existing `template-pricing-bento`.
10. **Timeline / roadmap** → existing timeline templates.
11. **Tabular data, ≥2 columns** → existing table templates.
12. **3–8 distinct features/phases without clear hero** → existing bento2-6 or rebuild.
13. **Anything else with a 2-row+ heading** → text-only fallback (`template-info-left-middle`, `template-bullets-N`).

**Bento + full-bleed are step-2-and-3 of the priority list.** Bullets/info templates are step-13. They no longer compete head-to-head.

### "Creative mix" directive

For decks of **≥6 content slides**, the generator must vary patterns:
- No more than **3 of any single pattern in a row**.
- No more than **60% of content slides** use any one pattern.
- Tables, quotes, and chapter dividers count toward variety.

For decks under 6 content slides, this directive does not apply (a 4-slide deck of all pentagrids is fine if the content fits).

The aim: a deck that breathes between bento, full-bleed, and tabular content rather than 14 pentagrids in sequence.

## Divider rule (clarified)

Add to `design-system.md` "List Row Pattern" section:

> **Dividers belong only inside the List Row pattern.** Bento cards, pillar grids, pentagrids, and image-bento-mix layouts must not place 1px Gray/200 dividers between cards or rows. The 32px gutter is the only separator. If a slide has dividers visible and is not a List Row layout, it is a generation bug — re-run with the correct pattern.

## FIG placeholder integration

Each pattern's image slot uses the existing FIG placeholder spec from `design-system.md`:
- Card bg: Gray/100 (light) or Gray/900 (dark)
- Inner dashed outline: Gray/300 (light) or Gray/600 (dark), 1px, dashPattern [8,8], 16px corner radius, inset 16px
- Top-right Fig label: 14 Regular Gray/500
- Optional bottom-left caption-label: 16 Medium Gray/700 (sm cards), 24 Medium (lg/hero cards)

When the asset library has a matching item (per `assets/library.json` tags), copy the fill into the slot **and remove both the dashed outline rectangle and the Fig label text node** — the dashed treatment is the visual signal that the slot is empty. When no match exists, ship the placeholder as-is so the missing asset is unmistakable in the deck review.

## File changes (summary)

| File | Change |
|---|---|
| `templates/registry.json` | Add `chrome` block. Add `layoutPatterns` block listing the 5 patterns with `name`, `referenceNodeId`, `contentSignature`, `slotComposition`, `imageSlotCount`. |
| `templates/design-system.md` | Add "Layout Patterns" section with build functions for each of the 5 patterns. Add `applyChrome()` and `auditChrome()` to "Canonical text helper" section. Tighten divider rule in "List Row Pattern" section. |
| `.claude/commands/generate-presentation.md` | Rewrite Step 4 matching priority. Add Step 5b sub-step requiring `applyChrome()` + `auditChrome()`. Add "Creative mix" directive. |

No changes outside these three files. Generator stays MCP-first, Claude-as-engine.

## Validation — proof this works

The 5 patterns were built in the Bluewater Figma file using `applyChrome` + `auditChrome`. After build, `auditChrome` was called on all 5 slides:

```json
{
  "Pattern 1 — full-bleed-hero":   [],
  "Pattern 2 — split-portrait":    [],
  "Pattern 3 — pentagrid":         [],
  "Pattern 4 — image-pillar-grid": [],
  "Pattern 5 — image-bento-mix":   []
}
```

Zero issues across all 5 patterns. Screenshots confirm visual correctness. Reference page: `57300:2`.

A prior naive build (without the helpers) had every meta + title at (0,0) due to a parent-layout-mode check bug. The audit would have caught all of those failures. The systemic fix is what makes the difference, not the patterns themselves.

## Out-of-scope — flagged for later

- **Asset library expansion.** The asset library currently has one synced item (`cafe-station-1-hero`). FIG placeholders cover the gap, but the patterns shine when real imagery is available. A separate task should expand the library.
- **Pattern-to-reference matching.** When the generator picks a pattern, it could optionally compare its output to the `referenceNodeId` (via `get_screenshot`) and flag visual deviations. Useful but not required for the first ship.
- **PowerPoint export.** Phase 2.
