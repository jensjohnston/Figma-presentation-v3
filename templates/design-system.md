# Bluewater Design System

Rules for building Bluewater presentation slides. Read alongside `registry.json` (the machine-readable mirror of this spec).

Slides are built from scratch using the rules below. No template-first approach — every slide picks card widths from the 6-unit macro grid and applies the tier's typography.

**How this document is organized:**
1. **Layer 1: Typescale** — every legal font size.
2. **Layer 2: Card size tiers** — each card's typography, padding, itemSpacing by width.
3. **Layer 3: Impact overrides** — content-triggered step-ups for dramatic numbers.
4. **Grid system** — slide geometry, margins, vertical rhythm.
5. **Patterns** — bento cards, list rows, FIG placeholders, dark slides, data viz, etc.
6. **Conventions** — auto-layout, text-node naming, frame naming.

Read bottom-up: "what card am I in?" → tier → defaults. "Does content qualify for impact?" → step heading up one size.

---

## Layer 1: The Typescale

**Scale:** Minor Third (1.2 ratio), rounded to whole pixels.

```
12 · 14 · 16 · 18 · 20 · 24 · 28 · 32 · 36 · 40 · 48 · 56 · 64 · 80 · 96
```

Every font size MUST come from this scale. No exceptions.

**Font:** Suisse Int'l
**Weights:** Semi Bold, Medium, Regular

### Line heights

**Line heights are ALWAYS declared in percent, never in pixels.** Figma API: `{ unit: 'PERCENT', value: N }`.

Three tiers, tightened as text gets larger:

| Size range | Line height | Role |
|---|---|---|
| ≤24px | **134%** | Body, labels, subtitle — multi-line readability |
| 28–40px | **115%** | Bento headings — short and solid |
| ≥48px | **110%** | Display, slide title, hero heading — tight leading looks intentional |

**Exception:** the slide-level eyebrow (32 Medium, above slide title) uses **110%** — it's display-adjacent and anchors tight to the title block.

---

## Layer 2: Card Size Tiers

Every bento card falls into one of five tiers based on its width AND height.

### Tier definitions

| Tier | Width | Height | When |
|---|---|---|---|
| **xs** | <=272px (1 unit) | Any | Single-unit cards |
| **sm-compact** | 273-576px (2 units) | <500px | Half-height cards, dense layouts (pricing, timeline) |
| **sm** | 273-576px (2 units) | >=500px | Standard bento cards with image space |
| **lg** | 577-880px (3 units) | Any | Wide bento cards |
| **hero** | Any size, blue or dark bg | Any | The one emphasized card per slide |

**How to pick the tier:** Check width first, then height. A 576px-wide card that's 776px tall (bento grid) uses **sm**. The same 576px-wide card at 394px tall (half-height, custom layout) uses **sm-compact**.

### Typography per tier

Two hard rules govern this table:
1. **Label size = body size in the same card.**
2. **Body weight is Medium. Heading weight is Semi Bold.** No exceptions by tier.

| Element | xs | sm-compact | sm | lg | hero |
|---|---|---|---|---|---|
| Label | 16 Medium 134% | 16 Medium 134% | 24 Medium 134% | 24 Medium 134% | 24 Medium 134% |
| Heading | 24 Semi Bold 134% | 28 Semi Bold 115% | 36 Semi Bold 115% | 36 Semi Bold 115% | 56 Semi Bold 110% |
| Body | 16 Medium 134% | 16 Medium 134% | 24 Medium 134% | 24 Medium 134% | 24 Medium 134% |
| Caption | 14 Regular 134% | 14 Regular 134% | 14 Regular 134% | 14 Regular 134% | 14 Regular 134% |

**`caption`** is for tiny supporting text inside cards or diagrams — e.g. chart min/max labels, figure labels ("Fig 05.A"), dimension callouts ("1200 mm"), list-row markers. Use Regular weight (not Medium) so it reads as subordinate to the label and body.

### Stat-row exception

A 4-column stat row (like slide 6 Performance) always uses **sm tier** (label 24 / body 24) regardless of whether the column height falls under the 500px sm-compact threshold. This keeps labels legible against the large impact numbers typical of stat layouts.

### Stat-card exception (inner padding)

A **stat card** is a card whose dominant element is a display-scale impact number (64px+). When a card qualifies:
- **Inner X padding: 32px** (down from the tier default of 48px)
- **Inner Y padding: 48px** (unchanged — top+bottom stay at tier default)
- Y padding unchanged so the top label row and bottom caption still sit at the standard 48px from the edges.

Rationale: large display numbers (e.g. "1K", "10K", "100K+", "3L", "98%") need more lateral breathing room inside the card. 32px X padding lets the number extend further toward the card edges without colliding with decorative chrome, and gives the whole card a denser, more typographic feel appropriate for stat content.

Applies to: slide 22 scenarios, slide 6 performance, and any future card where the impact number is the hero element. Does **not** apply to list rows, bullet cards, or content-heavy cards where text paragraphs dominate.

### Marker sizing

A **marker** is a small number or letter (01, 02, A, B) that indexes a card or list row. Two sizing patterns:

| Context | Size | Example |
|---|---|---|
| **Card marker** — single marker at the top of a card, matches the card's label size | 16 Medium 134% (xs / sm-compact) · **24 Medium 134%** (sm / lg / hero) | Slide 3 "01/02/03" on each Produce/Store/Distribute card; Slide 13 "01–04" on each benefit card |
| **Dense marker** — marker inside a bullet list, list-row, or stacked ordinal list; one typescale notch smaller than the surrounding body | 14 Regular 134% (xs-scope) · **20 Medium 134%** (lg-scope) | Slide 7 / 9 list-row markers; Slide 11 hero card bullet markers |

Rule of thumb: if the marker introduces a card, it matches the label size. If the marker indexes items in a dense list, it steps down one notch.

### Padding & spacing per tier

| | xs | sm-compact | sm | lg | hero |
|---|---|---|---|---|---|
| Inner padding | 24px | 24px | 48px | 48px | 48px |
| `itemSpacing` (auto-layout) | 12px | 12px | 16px | 16px | 16px |

Use a single `itemSpacing` per card so auto-layout remains consistent. If label↔heading and heading↔body need different gaps, use nested auto-layout frames — don't special-case individual text nodes.

**Stat-card override:** cards with a dominant impact number (64px+) use **32px X padding** regardless of tier — see "Stat-card exception" above.

### Slide-level text (outside cards)

| Element | Size | Weight | Line height | Color |
|---|---|---|---|---|
| Slide title | 64 | Semi Bold | 110% | Gray/900 #18181B |
| Slide eyebrow (above title) | 32 | Medium | 110% | Gray/700 on light · Blue/600 on dark |
| Slide subtitle | 28 | Medium | 134% | Gray/500 #71717A |
| Slide body (the `body` node, under the title) | 28 | Medium | 134% | Gray/500 #71717A |
| Slide hero body (primary text, no competing title) | 40 | Medium | 134% | Gray/500 #71717A |
| Slide paragraph | 16 | Medium | 134% | Gray/500 #71717A |
| Top meta | 14 | Regular | 134% | Gray/500 #71717A |

**`body` = supporting copy (28px).** The node named `body` that sits directly under the slide title is a subtitle: **28 Medium 134% Gray/500**, positioned **15px below the title** (title bottom y=185 → body y=200), content width. When the body sits **beside** the title instead (top-right header paragraph), it is **top-aligned with the title (y=115)** in a fixed right column **587px wide, flush to x=1872 (starts x=1285), left-aligned**; the title's left region then caps at ~1205px so the two don't collide. A **hero body** — the slide's primary text with no competing 64px title (e.g. `full-bleed-hero`) — steps up to **40px**. The old 32px subtitle and 20px deck deviations are retired; do not propagate them when cloning.

> ⚠️ **Source of truth.** When this doc, `registry.json`, and a built slide disagree, the **Template references page (`56881:463`) wins** — specifically `pillar-grid-3up-functional` / `pillar-grid-3up-product-with-body` (title 64 / body 28 / 15px gap). Verify against those frames before trusting any single slide.

**`slide-paragraph`** is supporting context text below a bento row — for example the "Onboard purification runs continuously…" line beneath a stat row. Use it when the content is a short paragraph that explains or qualifies the bento above, not a full subtitle.

**No bottom meta.** Slides end at the content. The 48px bottom padding is the only space below the last content element. Do not place page counters or section labels at the bottom — they live in the top meta row only.

**Titles end with a period.** Every slide title/headline ends in a full stop (brand rule, shared with the newsletter renderer) — e.g. "Reverse osmosis in plain English." — **unless** it already ends in terminal punctuation (a question "…Safe?" or "!"). Applies to the `title` node and hero headings; not to eyebrows, subtitles, body, labels, or meta. When cloning a template, add the period if the source title lacks one.

**Long-title cap:** Slide titles may wrap to **maximum 2 rows** at 64 Semi Bold 110%. If the content won't fit in 2 rows, shorten the title or split it into a shorter title plus a `subtitle`. 3+ row titles are not allowed.

**No widows (multi-line titles & display text):** a wrapped title (or any large display string) must never leave a **single word alone on the last line** — e.g. "Reverse osmosis in plain / English" is wrong. Bind the final 2–3 words with **non-breaking spaces** (` `) so the last line carries at least two words ("Reverse osmosis / in plain English"). Do not force the wrap with manual line breaks (`\n`) — that breaks at fixed widths and re-breaks badly if the text or container changes. Bind words, let it reflow. Applies to titles, hero headings, and any 2-line display copy.

**Prose max-width (body paragraphs):** body/paragraph copy must read as prose, not a narrow ribbon. Two canonical widths: a `body`/`subtitle` **under** the title uses content width (full or to the card edge); a paragraph **beside** the title (top-right header column) uses the fixed **587px** column flush to x=1872 (starts x=1285), 28 Medium 134%. Never leave a header paragraph at an arbitrary narrow width (e.g. 410px) — it wraps into an awkward column. If a one-off needs a custom width, cap it around a 50–75 character measure.

Chrome positioning and title spacing rules are defined in the Grid System section below (Vertical rhythm).

### Color system

Four token scales from the design system: Gray, Blue, Rose, Green (each 50-950).

**Gray scale:**

| Token | Hex |
|---|---|
| Gray/White | #FFFFFF |
| Gray/50 | #FAFAFA |
| Gray/100 | #F4F4F5 |
| Gray/200 | #E4E4E7 |
| Gray/300 | #D4D4D8 |
| Gray/400 | #A1A1AA |
| Gray/500 | #71717A |
| Gray/600 | #52525B |
| Gray/700 | #3F3F46 |
| Gray/800 | #27272A |
| Gray/900 | #18181B |
| Gray/950 | #09090B |

**Blue scale:**

| Token | Hex |
|---|---|
| Blue/50 | #F0F5FF |
| Blue/100 | #DBEAFE |
| Blue/200 | #BFDBFE |
| Blue/300 | #93C5FD |
| Blue/400 | #60A5FA |
| Blue/500 | #3B82F6 |
| Blue/600 | #2563EB |
| Blue/700 | #1D4ED8 |
| Blue/800 | #1E40AF |
| Blue/900 | #153E88 |
| Blue/950 | #00205B |

**Rose** (contextual — health topics only): primary accent **Rose/600 `#EC003F`**. Full scale available in `registry.json` if ever needed.

**Green** (contextual — sustainability topics only): primary accent **Green/600 `#17A34A`**. Full scale available in `registry.json` if ever needed.

**Presentation color roles:**

| Role | Token | Hex |
|---|---|---|
| Headings | Gray/900 | #18181B |
| Labels/eyebrows | Gray/700 | #3F3F46 |
| Body copy | Gray/500 | #71717A |
| Card backgrounds | Gray/100 | #F4F4F5 |
| Slide background | White | #FFFFFF |
| Hero card bg (blue) | Blue/600 | #2563EB |
| Dark card bg | Gray/900 | #18181B |
| Text on blue/dark | White | #FFFFFF |
| Label on dark card | Blue/600 | #2563EB |
| Badge (savings) | Green/600 | #17A34A |
| Health context | Rose/600 | #EC003F |
| Sustainability | Green/600 | #17A34A |

**Color rules:**
- Rose and Green are **contextual** — only when content is about health or sustainability
- Blue is used sparingly: hero cards and accent dots only
- All other UI is grayscale

### Valid text combinations per cell

Use the minimum needed:

1. **Heading only** — bold statement ("3 machines", "Entrance")
2. **Eyebrow + Heading** — labeled content ("Now" + "Order bottles")
3. **Heading + Body** — title with detail ("Entrance" + "Door wrap + floor trail stickers")
4. **Eyebrow + Heading + Body** — full stack ("Primary" + "Health-conscious" + "Read labels...")
5. **Body only** — rare, for footnotes or supporting context

**Rule:** Hide unused text elements (`visible = false`), never fill them with spaces. After hiding a slot, **re-anchor** any container that should stay bottom-justified — see the [Bottom-anchor rule](#bottom-anchor-rule-re-justify-after-hiding-content). Hiding a slot inside a hugging auto-layout frame shrinks the frame but leaves it pinned at its top, floating the rest mid-region.

---

## Layer 3: Impact Overrides

When a card's content is a **single dramatic number or 3-word punchy phrase** (e.g. "3L", "98%", "Any"), step the heading up one size on the typescale above the tier default. Body and label stay at tier default.

**Card-heading default is 36 (sm/lg tier).** When the heading itself is a **single word or ≤3-word phrase** carrying the card (e.g. "Hydrate.", "Energy.", "Install", "Service"), use **48 Semi Bold 110%** — the one sanctioned step above 36 for headings (skip 40). Canonical examples: `pillar-grid-3up-functional`, `numbered-list`. Every other standard card heading stays **36**; do not use 32 (a retired deviation). Small cards (xs/sm-compact) keep their tier headings (24/28), hero cards 56.

**Constraints:**
- **Max one impact element per card.**
- **Max one hero card per slide.**
- Body copy, labels, and multi-line headings never get impact treatment.
- If the slide has 5+ cards, scale heading **down** instead of up.

---

## Grid System

All custom slides use a **12-column grid with a 6-unit macro grid layered on top**.

```
Slide: 1920 x 1080px
Horizontal margin: 48px each side
Top margin: 48px (top meta at y=48)
Bottom margin: 48px (last content element bottom edge at y=1032)
Gutter: 32px
Usable width: 1920 - 96 = 1824px
```

### Vertical rhythm

```
y=0    ─────────────── slide top
y=48   ─── top meta (14 Regular, height ~19 → bottom ~67)
       ↕ 48px gap
y=115  ─── slide title (64 Semi Bold 110%, 70px per line)
       ↕ 15px gap (fixed)
y=200  ─── slide body / subtitle (32 Medium 134%, when present)
       ↕ variable gap — absorbs title + body height
y=287  ─── content starts (FIXED)
       ...
y=1032 ─── last content element ends (content height always 745px)
y=1080 ─────────────── slide bottom
```

- **Meta → title gap: 48px** (between meta bottom edge and title top)
- **Content is pinned at y=287** regardless of title length — card height is always **745px**
- **Title → content gap varies** to absorb the title's line count:
  - 1-row title (70 tall) → ~102px gap to content
  - 2-row title (141 tall) → ~32px gap to content
- This gives card-height consistency across the deck without forcing title authors to keep titles on one line
- **No bottom meta.** The 48px bottom margin is the only space below the last content element.

### 12-column fine grid

```
Usable width: 1824px
Column width: ~123px (1824 ÷ 12 cols with 32 gutters — slight rounding tolerance)
Gutter: 32px
```

Every vertical edge in the design should align to a 12-col position or gutter. Use this for fine alignment of text, icons, inline elements.

### 6-unit macro grid (bento card sizing)

Cards expand to fill the 1824 usable width. Standard tier widths:

| Tier | Width | Notes |
|---|---|---|
| xs | 277px | 1 macro unit |
| sm | 587px | 3 cards + 2 gutters = 1825 (≈ 1824, 1px tolerance) |
| lg | 896px | 2 cards + 1 gutter = 1824 ✓ exact |
| full | 1824px | Full-bleed, flush to margins |

**Rule:** Card edges always align to margins (x=48 on the left, x=1872 on the right). Text and inline elements inside cards can align to any position.

### Vertical rules (enforced religiously)

- Top margin: **48px** (top meta at y=48)
- Bottom margin: **48px** (last content element's bottom edge at y=1032)
- Horizontal margin: **48px** each side (content between x=48 and x=1872)
- Meta → title: **48px** gap (title top edge at y=115)
- Title → body/subtitle: **15px** gap (body at y=200 when present); body is **32 Medium 134% Gray/500**, full width
- Content top: **y=287 (FIXED)** — does not shift based on title length
- Card height: **745px** (= 1032 − 287)
- Title → content gap: **variable** — computed as `287 − (title_y + title_height)`. Typically ~102 for 1-row titles, ~32 for 2-row titles.

### Row heights within the content area

Content area is always 745px tall (y=287 → y=1032). When a slide has multiple rows:

- **2 equal rows**: (745 − 32) / 2 = **356px** each (32 gutter between)
- **3 equal rows**: (745 − 64) / 3 = **227px** each
- **Asymmetric**: the hero or primary row takes more height; supporting rows compress

Single-row slides use the full 745px.

### Bottom-anchor rule (re-justify after hiding content)

Template content regions are designed so the **last visible element's bottom edge sits at y=1032** (48px from the slide bottom), or **48px above a card/column's bottom edge** for content inside a card. This is the "justified-between" look: chrome/heading pinned to the top, primary copy or stat pinned to the bottom.

**The pitfall (why slides drift mid-region):** most template containers are **auto-layout frames that HUG their content**. When you hide an optional slot (`visible = false`) or remove a child, the frame shrinks — but it stays pinned at its original **top** `y`, so the remaining content floats in the middle of the region instead of dropping to the bottom. No error is thrown; the slide is just silently wrong.

**The rule:** after hiding or removing any optional slot, **re-anchor** the affected container so its bottom edge returns to the design position:

```js
// slide-level block (direct child of the slide frame): bottom edge → y=1032
block.y = 1032 - block.height;

// in-card block (child of a card/column): bottom edge → 48px above the card bottom
block.y = (cardHeight - 48) - block.height;   // cardHeight = 745 for a full-height column
```

Re-read `block.height` AFTER the slot is hidden — an auto-layout frame only reports its shrunken height once the child is invisible.

**Currently tagged** (`bottomAnchored` in `registry.json`, applied automatically by `anchorBottom`): `split-portrait` (body → slide bottom), `comparison-3up` and `unit-economics-3up-scaling` (per-column metric/caption block → 48px above card bottom), `pillar-grid-3up-pricing` (per-column price block → 48px above card bottom). A coverage sweep verified that bento grids, pillar-grid product/functional/with-body, tables, timelines, metrics-4, checklist-bento, and pillar-grid-4up-image are **top-aligned or absolutely positioned** and do **not** float — so they need no tag. Always applies to **every escape-hatch build**. If you hid a slot and did not re-anchor, treat the slide as broken even though nothing errored. Pair this with `auditChrome` as a standing post-build check; when a newly-used template floats on slot-hide, add a `bottomAnchored` entry after verifying its frame name.

## Auto-layout

**Auto-layout is the default** for cards, card rows, and text stacks. Use Figma auto-layout frames so spacing stays correct when content changes. Absolute positioning is allowed only when it produces a better result (e.g., dimension labels on technical diagrams, decorative graphics inside FIG placeholders, bar/tick elements inside a stat card's range widget). Default to auto-layout; reach for absolute positioning consciously.

## Bento Card Construction

- **Corner radius:** 32px
- **Gap between cards:** 32px
- **Background:** Gray/100 (#F4F4F5) standard, Blue/600 (#2563EB) hero, Gray/900 (#18181B) dark/closing, White (#FFFFFF) on gray slide backgrounds
- **No drop shadows** (clean, flat aesthetic)
- **Clip content:** always true
- **Inner padding:** per card tier (see Layer 2)

### Card anatomy (vertical auto-layout)

Canonical stack for a bento card:

```
card (vertical auto-layout, padding per tier, itemSpacing 16)
├─ label       (tier label size)
├─ heading     (tier heading size)
├─ [flex spacer — OPTIONAL]
└─ body        (tier body size)
```

The flex spacer is **context-dependent**. Use it when the body should sink to the card's bottom edge (e.g., hero card with large impact number at top, supporting line at bottom). Omit it when body sits tightly below the heading with the default `itemSpacing`.

### Text node naming convention

Each text node inside a card or list row must be named by its **role**, not by its content. This lets automation and downstream tooling update typography reliably by role.

| Context | Allowed names |
|---|---|
| Card or list row | `label`, `heading`, `body`, `caption` |
| Slide-level | `meta`, `eyebrow`, `title`, `subtitle`, `slide-paragraph` |

**Rule:** Do not reuse `label` for what is actually a `heading` (common mistake when a short phrase sits prominently on a card). If the node is the dominant typographic element on the card, it's a `heading`. If it's the small text above the heading, it's a `label`. If it's tiny supporting text below, it's a `caption`.

### Frame naming convention

Every slide frame is named **`Slide NN — Topic`** (e.g. `Slide 03 — Proposition`). `NN` is the zero-padded two-digit slide number; Topic is a short descriptor matching the slide's content.

Card frames inside a slide are named by their role (`card-1`, `card-2`, `hero-card`, `supporting-card`, `fig-card`, `stat-card`, etc.). Row frames use `bento-row`, `stats-row`, `config-row`, `stage-row`, `use-case-list`, `benefits-grid`.

### No motion

Slides are static. No animations, transitions, or motion effects as part of the design system. Any motion that ships with an exported deck is handled by the playback tool (Keynote, PPT, etc.), not specified here.

### Escape hatch

If a slide's content doesn't fit any card tier, list-row pattern, or documented template, build the one-off deliberately:
- Keep the chrome (top meta y=48, title at y=115, content at y=287) untouched.
- Use typography sizes from Layer 1 only — no off-scale sizes.
- Use colors from the token scales only.
- Document the deviation in the slide frame's name (e.g. `Slide 12 — Combined System · custom flow diagram`) so it's clear later why the slide broke the grid.

One-offs are fine; ad-hoc typography or colors are not.

## Dark slide pattern

Title and closing slides (openers, section reveals, closings) invert the system:

- Slide background: **Gray/900** (`#18181B`)
- Title and body text: **White**
- Eyebrow (above title): **Blue/400** (not Blue/600 — Blue/600 is too close to Gray/900 for legibility)
- Meta / page counter: **Gray/500** (muted but legible)
- Layout follows the same vertical rhythm (meta y=48, title y=115, content y=287)

Use dark slides only for chrome moments: opening title, section-break reveals, closing. Body content slides stay light.

## FIG placeholder pattern

When a slide reserves space for a render or image that will drop in later (e.g. slide 5 tank truck, slide 11 trailer), use a **FIG placeholder card**:

- Card background: **Gray/100** (standard card bg)
- Inner dashed outline: **Gray/300**, 1px, `dashPattern: [8, 8]`, 16px corner radius
- Top-right label: `Fig NN.A` in **14 Regular Gray/500** (caption tier)
- Bottom-left `ft` + `fd` descriptors (24 SB + 18 Regular) describing what the render will show

When the real render arrives, it replaces the inner dashed area. The outer card stays.

## Data viz & diagram principles

For charts, bars, technical drawings, and custom visualizations (slide 6 stats, slide 9 IBC drawing, slide 10 truck config cells, slide 11 trailer):

- **Labels inside the viz** use caption typography: 14 Regular 134% Gray/500 (dimension callouts, scale ticks, figure labels)
- **Grid / scaffolding lines**: Gray/200 at 50% opacity for subtle; Gray/300 for more prominent
- **Accent / highlight**: Blue/600 (fills, filled cells); Blue/200 with 50% opacity for fills that shouldn't dominate
- **Neutral strokes**: Gray/400 for 1px neutral strokes (trailer outline, generic shape edges); Gray/900 2px for structural outlines (IBC tank outer)
- **Ground / axis lines**: Gray/900 2px (on light bg); White 50% (on dark bg)
- No shadows, no gradients, no rounded corners beyond 4px on small cells

Case-by-case detail is OK; this section is the baseline palette, not a full per-chart spec.

## List Row Pattern

Tabular content (like slide 7 Use Cases or slide 9 IBC specs) uses a **list row** pattern — one step smaller than lg cards so the row reads tabular, not card-like:

```
row (horizontal auto-layout, no fill, no padding)
├─ marker  (20 Medium 134%)
├─ heading (32 Semi Bold 115%)
├─ [flex spacer]
└─ body    (20 Medium 134%, right-aligned)
```

Between rows, use a 1px Gray/200 divider. Row height is content-driven (HUG).

Rationale: a list row is denser than a bento card. Stepping heading down from 36→32 and marker/body from 24→20 keeps rows scannable and visually distinct from cards.

**Divider scope (strict):** dividers belong **only inside the List Row pattern**. Bento cards, pillar grids, pentagrids, and image-bento-mix layouts must not place 1px Gray/200 dividers between cards or rows. The 32px gutter is the only separator. If a generated slide has dividers visible and is not a List Row layout, that's a generation bug — pick a different pattern.

## Flexible Item Counts

**Fewer items:** Hide unused cells or build from scratch. Never use filler text.

**More items:** Build from scratch using the grid system. Same visual style.

| Items | Layout | Grid |
|---|---|---|
| 2 | 2 equal columns | 3u + 3u |
| 3 | 3 equal columns | 2u + 2u + 2u |
| 4 | 2x2 grid | (3u + 3u) x 2 rows |
| 5 | 2+3 or 3+2 | top: 2u+2u+2u, bottom: 3u+3u |
| 6 | 2x3 or 3x2 | (2u+2u+2u) x 2 rows |
| 7-8 | 4x2 grid | (varies) x 2 rows |

Timelines: 3-8 steps. Beyond 8, split across slides.
Bento grids: 2-6 cells. Beyond 6, content gets too small.

## Creative Decision Guide

1. **How many cells?** Look up Flexible Item Counts for the row/grid shape.
2. **What tier does each cell fall into?** Look up Layer 2 for typography and padding.
3. **Is there one number or fact that should dominate?** Check Layer 3 impact rules.
4. **Does every cell need all three of label/heading/body?** Probably not. Use the minimum combination.
5. **Is this a comparison?** Equal-width cells side by side.
6. **Is this tabular/list content?** Use the List Row pattern, not cards.
7. **Does the content break every tier?** Use the Escape Hatch — document the deviation and ship the one-off.

## Canonical text helper (prevents autosizing bugs)

Figma's `textAutoResize` modes are order-sensitive. Setting `resize()` before the mode, or setting the mode before `characters`, leads to stuck `height=1` nodes that render clipped or invisibly thin. Always use this helper when building text in a `use_figma` script:

```js
// Put this near the top of every slide-building script.
// Assumes FONT is defined and all needed styles are preloaded with figma.loadFontAsync.
function mkText(parent, chars, opts) {
  const {
    size,
    style   = "Regular",     // "Regular" | "Medium" | "Semi Bold"
    color,                   // {r,g,b} 0–1
    x = 0, y = 0,
    lh = 134,                // percent; use 110 for titles/eyebrows, 100 for display numbers
    width,                   // if set: HEIGHT mode with fixed width, auto-height
    align = "LEFT"           // "LEFT" | "CENTER" | "RIGHT"
  } = opts;

  const t = figma.createText();
  parent.appendChild(t);

  // 1. typography
  t.fontName   = { family: FONT, style };
  t.fontSize   = size;
  t.lineHeight = { unit: "PERCENT", value: lh };
  t.fills      = [{ type: "SOLID", color }];
  t.textAlignHorizontal = align;

  // 2. CONTENT FIRST — must be set before changing textAutoResize
  t.characters = chars;

  // 3. mode AFTER content
  if (width != null) {
    t.textAutoResize = "HEIGHT";            // width fixed, height auto
    t.resize(width, t.height);              // pass current (auto-computed) height
  } else {
    t.textAutoResize = "WIDTH_AND_HEIGHT";  // HUG both
  }

  // 4. position last (resize may have nudged it)
  t.x = x; t.y = y;
  return t;
}
```

**Critical rules:**
- Always set `characters` BEFORE `textAutoResize`.
- Never use `textAutoResize = "NONE"` unless you explicitly want to clip text.
- When you need a fixed width, pass `width:` — the helper sets HEIGHT mode, which means the height auto-grows with wrapping lines.
- For a cap ("hug content but wrap if > N"), set `width: N` — HEIGHT mode treats N as the wrap boundary.

**Important gotcha:** when `parent` has `layoutMode === "VERTICAL"` or `"HORIZONTAL"` (auto-layout), Figma positions children automatically — setting `t.x` / `t.y` is ignored. The helper above silently sets x/y always, which is fine for direct slide-level placement. If you're appending text to an auto-layout block, omit `x` / `y` and let the layout position them.

## applyChrome — the only sanctioned way to place slide chrome

Chrome (top-meta and slide title) MUST go at exact positions defined in `registry.json` → `typography.chromePositioning`:

| Slot | x | y | Other |
|---|---|---|---|
| `meta-left`  | 48   | 48  | 14 Regular, Gray/500 (light) or Gray/400 (dark) |
| `meta-right` | 1872 - width | 48 | 14 Regular, RIGHT-aligned, same color tier |
| `title`      | 48   | 115 | 64 Semi Bold 110%, Gray/900 (light) or White (dark), max 2 rows |

> ⚠️ **`meta-right` must be RIGHT-anchored — re-pin after editing its text (clone path).** `meta-right`'s **right edge belongs at x=1872** (48px from the slide edge). Some templates ship it **LEFT-aligned at a fixed x** (e.g. tables, comparison, timeline pin it at x=1659 to match a placeholder width). When you clone such a template and replace the text, a left-aligned hugging box keeps its left x and the right edge **drifts** — a shorter string lands ~105px from the slide edge instead of 48px. After setting `meta-right` text on a cloned template, always re-pin: `m.textAlignHorizontal = "RIGHT"; m.x = 1872 - m.width;` (load the font first — alignment is a font-dependent mutation). `applyChrome` already does this for from-scratch builds; the clone path must do it explicitly. `meta-left` is LEFT-anchored at x=48 and grows rightward, so it never needs re-pinning.

**Never hand-position chrome elements in a from-scratch build.** Use this helper:

```js
function applyChrome(slide, opts) {
  const {
    metaLeftText  = "Bluewater",
    metaRightText = "Official hydration partner of Volvo",
    titleText,                 // omit when the layout has no slide-level title (full-bleed, pentagrid, cover)
    titleWidth = 1824,         // 880 for split-portrait variants (title fits half-slide width)
    isDark = false,            // dark slide bg → lighter meta + white title
  } = opts;

  const grayMeta  = isDark ? { r: 0xA1/255, g: 0xA1/255, b: 0xAA/255 } : { r: 0x71/255, g: 0x71/255, b: 0x7A/255 };
  const titleClr  = isDark ? { r: 1, g: 1, b: 1 }                       : { r: 0x18/255, g: 0x18/255, b: 0x1B/255 };

  const meta = mkText(slide, metaLeftText, {
    size: 14, style: "Regular", color: grayMeta, x: 48, y: 48, name: "meta-left",
  });

  let metaR = null;
  if (metaRightText) {
    metaR = mkText(slide, metaRightText, {
      size: 14, style: "Regular", color: grayMeta, name: "meta-right",
    });
    metaR.x = 1872 - metaR.width;
    metaR.y = 48;
  }

  let title = null;
  if (titleText) {
    title = mkText(slide, titleText, {
      size: 64, style: "Semi Bold", color: titleClr, lh: 110,
      width: titleWidth, x: 48, y: 115, name: "title",
    });
  }

  return { meta, metaR, title };
}
```

## auditChrome — validate before returning

After every from-scratch slide build, call `auditChrome(slide)`. It validates meta + title positions **and** that the slide `body` is 32px with a 15px title gap. If the issues array is non-empty, fix the offending nodes before returning:

```js
function auditChrome(slide) {
  const issues = [];
  const m  = slide.children.find(n => n.type === "TEXT" && n.name === "meta-left");
  const mR = slide.children.find(n => n.type === "TEXT" && n.name === "meta-right");
  const tt = slide.children.find(n => n.type === "TEXT" && n.name === "title");

  if (m && (m.x !== 48 || m.y !== 48))
    issues.push({ node: "meta-left", at: [m.x, m.y] });
  if (mR && (Math.round(mR.x + mR.width) !== 1872 || mR.y !== 48))
    issues.push({ node: "meta-right", rightEdge: Math.round(mR.x + mR.width), y: mR.y });
  if (tt) {
    if (tt.x !== 48 || tt.y !== 115)
      issues.push({ node: "title", at: [tt.x, tt.y] });
    const maxH = 64 * 1.1 * 2 + 1;  // 64 SB at 110% line height, max 2 rows
    if (tt.height > maxH)
      issues.push({ node: "title", reason: "exceeds 2 rows", h: tt.height, maxAllowed: maxH });
  }

  // body / subtitle directly under the title: must be 32px, 15px below the title
  const bd = slide.children.find(n => n.type === "TEXT" && n.name === "body");
  if (bd) {
    if (bd.fontSize !== 32)
      issues.push({ node: "body", reason: "size must be 32", size: bd.fontSize });
    if (tt && Math.round(bd.y - (tt.y + tt.height)) !== 15)
      issues.push({ node: "body", reason: "title→body gap must be 15", gap: Math.round(bd.y - (tt.y + tt.height)) });
  }
  return issues;
}
```

**Documented chrome exceptions** (slide layouts that intentionally don't have a canonical title):
- `full-bleed-hero` — title anchored bottom-left over the image, NOT at y=115.
- `pentagrid-*` — title text lives inside the top-left card.
- `closing-pure-title` — title at y=400 (centered closing slide).
- `cover-with-product` — title nested inside layout, not as a direct child.

For these, omit `titleText` from `applyChrome()`. `auditChrome()` skips the title check when no `title` node exists at the slide root.

**Covers carry NO top-meta (hard rule).** Cover / title / opening slides have **no `meta-left` and no `meta-right`** — the brand lockup IS the content, so the top-meta row stays empty. Never put "Bluewater × …", a section label, or a page counter on a cover. When building a cover, skip `applyChrome` (or call it with no meta args) and do not add meta nodes; if you clone a template onto a cover, delete its `meta-left` / `meta-right`. The sequential page counter still treats the cover as slide 1 of N — it's simply not rendered on the cover, so content slides begin at `02 / N`. (Codified 2026-06-08 after the Culligan deck shipped a cover with `Bluewater × Culligan` · `01 / 08` meta.)

## The geometry contract — `auditFrame` (source guard) + `auditSlide` (output gate)

**Root cause of the 2026-05-29 JPD off-spec slides (now fixed at the root):** the generator clones template frames and only replaces text, so output is only as correct as the frame. There used to be two divergent sources of truth — the harmonized **Template references** page and the un-harmonized **Templates 4** page (`50285:14832`), whose frames shipped pre-harmonization geometry (title 80–120px, 64px margins, body 20–30px, cards ~80px off the bottom). Cloning a stale frame produced a silently off-spec slide.

**The root fix (2026-05-29 consolidation):** every generator template was harmonized and moved onto the **Template references** page; Templates 4 is `retired` / non-routable. There is now **one source of truth**, and it is verified — not assumed.

**Two guards keep it that way (the contract lives in `registry.json → slideContract`):**

1. **`auditFrame(frame, kind)` — the source guard (primary).** Audits a *template frame* against the contract + chrome presence. Run it over every registry template after any template edit; it must be empty for all. This catches drift at the source, so per-output repair is never needed. This is the standing regression test for the template library.

2. **`auditSlide(slide, kind)` — the output gate (defense-in-depth).** Run at the END of every generated slide. Because templates now conform, this should always pass; if it ever fails, a frame has drifted — fix the frame (run `auditFrame` to find which), don't patch the slide. `kind` is `"content"` (default), `"intro"` (title 96 / body 40), or `"skip"` (covers, heroes, full-bleed, closing, clones of finished slides, custom one-offs — exempt).

```js
// Mirror of registry.slideContract.
const CONTRACT = { metaY:48, titleX:48, titleY:115, titleSize:64, titleLH:110,
  contentL:48, contentR:1872, contentTopY:287, bottomY:1032,
  bodySize:28, introTitleSize:96, introBodySize:40 };

function auditSlide(slide, kind = "content") {
  if (kind === "skip") return [];
  const issues = [];
  const T = n => slide.findOne(x => x.type === "TEXT" && x.name === n);
  const title = T("title"), body = T("body");
  const ml = slide.findOne(x => x.type === "TEXT" && x.name === "meta-left");
  if (ml && Math.round(ml.y) !== CONTRACT.metaY) issues.push({ node:"meta-left", y:Math.round(ml.y) });
  if (title) {
    const want = kind === "intro" ? CONTRACT.introTitleSize : CONTRACT.titleSize;
    if (Math.round(title.fontSize) !== want) issues.push({ node:"title", size:Math.round(title.fontSize), want });
  }
  if (body) {
    const want = kind === "intro" ? CONTRACT.introBodySize : CONTRACT.bodySize;
    const bs = Math.round(body.fontSize);
    // card-internal bodies (24/16) are valid; only the slide-level body slot must hit `want`
    if (bs !== want && bs !== 24 && bs !== 16) issues.push({ node:"body", size:bs, want });
  }
  // content bounding box: direct children that are not chrome text and not the full-bleed bg
  let L=1e9, R=-1e9, B=-1e9, n=0;
  for (const c of slide.children) {
    if (c.type === "TEXT") continue;
    if (c.width >= 1900 && c.height >= 1000) continue;
    L=Math.min(L,c.x); R=Math.max(R,c.x+c.width); B=Math.max(B,c.y+c.height); n++;
  }
  if (n) {
    if (Math.abs(L - CONTRACT.contentL) > 1) issues.push({ content:"left", at:Math.round(L), want:CONTRACT.contentL });
    if (Math.abs(R - CONTRACT.contentR) > 1) issues.push({ content:"right", at:Math.round(R), want:CONTRACT.contentR });
    if (B < CONTRACT.bottomY - 12 || B > CONTRACT.bottomY + 8) issues.push({ content:"bottom", at:Math.round(B), want:CONTRACT.bottomY });
  }
  return issues;
}
```

**`auditFrame` — the source guard.** Same checks as `auditSlide` but run over the *template frames* themselves (and it also requires `meta-left` + `meta-right` to exist). Run it across every `registry.json → templates` entry whenever templates change; the issue list must be empty for all. This is what proves the single source of truth is intact.

```js
function auditFrame(frame, kind = "content") {
  const issues = auditSlide(frame, kind);            // reuse the same geometry checks
  if (kind !== "skip") {
    if (!frame.findOne(x => x.type==="TEXT" && x.name==="meta-left"))  issues.push({ node:"meta-left",  missing:true });
    if (!frame.findOne(x => x.type==="TEXT" && x.name==="meta-right")) issues.push({ node:"meta-right", missing:true });
  }
  // NOTE: left/centered/partial-width layouts (quotes, logo-garden, info-left-*, info-center, split-top)
  // legitimately don't span 48→1872 — treat their content L/R as informational, not failures.
  return issues;
}
```

**If `auditFrame` ever fails, fix the frame at the source** (snap title to 64@(48,115)/110, slide body to 28, content frame to x48/y287/w1824) and re-run the audit — never patch the cloned output per-slide. There is intentionally no routine "normalize the clone" step: the templates conform, so clones conform.

**Single source of truth (done).** All shapes the generator needs — 4/5/6-cell bento, NN-split, 50/50 comparison, N-bullet info, title/chapter, quote, huge-fact, metrics, logo, product, checklist, timeline — now exist as harmonized frames on the **Template references** page, grouped into labelled "Harmonized · …" sections. Templates 4 is retired. So there is nothing to normalize on clone: pick the references template, set text, run `auditSlide` as the regression gate. If a new shape is needed, build it on the references page to the contract and run `auditFrame` before adding it to the registry.

## Creative escape hatch

The presentation generator's primary path is **clone the closest reference template from the registry and replace text/image content**. Use this escape hatch only when no template fits — for example, content with 7+ distinct items, custom diagrams, or one-off pricing comparisons.

**Rules for from-scratch builds:**
1. **ALWAYS call `applyChrome()` first** with the right `metaLeftText` / `metaRightText` / `titleText` / `isDark` values.
2. **ALWAYS run `auditChrome(slide)` before returning.** Issues array must be empty.
3. **Use only typescale Layer 1 sizes** (12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 64, 80, 96). No off-scale sizes.
4. **Use only Gray / Blue / Rose / Green token scales.** No off-token colors.
5. **Use only 32px gap and 32px corner radius.** No 16px, 24px, 40px gutters.
6. **Use only 48px outer margins** (left, right, top, bottom).
7. **Auto-layout for all card stacks.** Card-internal text uses vertical auto-layout with the tier's `padding` and `itemSpacing`.
8. **Draw layout inspiration from frames on the Template references page** (id `56881:463`) — pick the closest pattern by content shape and adapt geometry.
9. **Document the deviation** in the slide frame's name: `Slide NN — Topic · Custom · <one-line reason>` (e.g., `Slide 12 — Combined System · Custom · 7-cell flow diagram`).

One-offs are fine; ad-hoc typography or colors are not.

## Text mode audit (safety net)

Run this at the end of any slide-building session to catch broken text nodes before the user sees them:

```js
// Walk every TEXT node on the current page. Flag likely-broken ones.
const page = figma.currentPage;
const issues = [];
(function walk(n) {
  if (n.type === "TEXT") {
    const expectedMinHeight = (typeof n.fontSize === "number")
      ? n.fontSize * ((n.lineHeight && n.lineHeight.value) ? n.lineHeight.value / 100 : 1) * 0.9
      : 10;
    if (n.textAutoResize === "NONE") {
      issues.push({ id: n.id, chars: n.characters.slice(0,40), reason: "mode=NONE" });
    } else if (n.textAutoResize === "HEIGHT" && n.height < expectedMinHeight) {
      issues.push({ id: n.id, chars: n.characters.slice(0,40), reason: `height ${Math.round(n.height)} < expected ${Math.round(expectedMinHeight)}` });
    }
  }
  if ("children" in n) for (const c of n.children) walk(c);
})(page);
return issues;
```

If `issues` is non-empty after a build, fix the offending nodes (usually by re-setting `characters` so `textAutoResize` auto-recomputes height) before moving on.

## Selecting existing nodes to modify (avoid collision bugs)

When a `use_figma` script edits nodes built by an earlier script, how you *identify* each node matters as much as how you mutate it. Finding nodes by a shared property (like `fontSize`) is fragile — the property may collide with an unrelated node in the same frame, and any mutation that changes that property partway through the script silently breaks the match.

**Real failure we've hit:** a script first bumped the slide's top supporting body to `fontSize=24`, then collected column references with `items.find(n => n.fontSize === 24)` at each column's x. Both the top body and the column-01 heading were fs=24 at x=48 — `.find()` returned the top body, and a subsequent `col.heading.y = 902` moved the top body down into the column area, breaking the slide.

**Rules for safe selection:**

1. **Prefer node names.** When building nodes, give each role a distinct `name` (`meta-left`, `col-01-heading`, `hero-title`). Retrieve later with a walker that matches on `name`.
2. **Prefer stable IDs across script calls.** `return { colHeadingIds: [...] }` from the build script and pass the literal IDs into the next `use_figma` call — node IDs don't change between runs, positions and children order can.
3. **If you must filter by properties, make the match unique.** Combine enough constraints that exactly one node matches: `fs===24 && width===420 && x===48`, not `fs===24` alone.
4. **Collect references BEFORE bulk-mutating a property you're filtering on.** If you plan to bump `fontSize=20 → 24`, snapshot all needed references first — never filter by fs again after the mutation.

**WRONG:**
```js
// Top body and col-01 heading both at x=48 both fs=24 after bump — .find() returns the wrong one
topBody.fontSize = 24;
const cols = COL_X.map(cx => {
  const items = slide.children.filter(n => Math.abs(n.x - cx) < 1);
  return { heading: items.find(n => n.fontSize === 24) };  // might be topBody!
});
```

**RIGHT:**
```js
// Option A — select first, then mutate
const cols = COL_X.map(cx => {
  const items = slide.children.filter(n => Math.abs(n.x - cx) < 1);
  return { heading: items.find(n => n.fontSize === 24) };  // fs still unique
});
topBody.fontSize = 24;  // mutation happens after refs are locked

// Option B — make the filter unique regardless of order
const col01Heading = slide.children.find(n =>
  n.type === "TEXT" && n.fontSize === 24 && n.width === 420 && Math.abs(n.x - 48) < 1
);

// Option C (best) — give nodes names at build time and match on name
// At build:  t.name = "col-01-heading";
// At edit:   const col01Heading = slide.findOne(n => n.name === "col-01-heading");
```
