# Bluewater Design System

This document defines the rules for building presentation slides. Read this alongside `registry.json` when generating slides.

**When to use templates vs. build from scratch:**
- Content fits a template perfectly -> clone and fill (fast)
- Content needs minor adaptation (hide a slot, skip body copy) -> clone, fill, hide unused slots
- Content needs structural change (different item count, custom layout) -> **build from scratch** using these rules

**How this document works — three layers:**
1. **Layer 1: Typescale** — every legal font size. If a size isn't on this scale, don't use it.
2. **Layer 2: Card Size Tiers** — look up the card width, get exact font sizes and padding.
3. **Layer 3: Impact Overrides** — content-triggered exceptions that swap heading sizes for larger steps.

Read bottom-up: "what card am I in?" -> tier -> defaults. "Does content qualify for impact?" -> override heading only.

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

Tighter as text gets larger:

| Size range | Multiplier | Rationale |
|---|---|---|
| 12-20px (body/labels) | size x 1.4 | Readable multi-line body copy needs air |
| 24-40px (headings) | size x 1.2 | Headings are short, tighter feels solid |
| 48px+ (display/impact) | size x 1.1 | Large text at tight leading looks intentional |

Full reference:

| Size | Line height | Tier |
|---|---|---|
| 12 | 18px | body |
| 14 | 20px | body |
| 16 | 22px | body |
| 18 | 26px | body |
| 20 | 28px | body |
| 24 | 28px | heading |
| 28 | 34px | heading |
| 32 | 38px | heading |
| 36 | 44px | heading |
| 40 | 48px | heading |
| 48 | 52px | display |
| 56 | 62px | display |
| 64 | 70px | display |
| 80 | 88px | display |
| 96 | 106px | display |

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

| Element | xs | sm-compact | sm | lg | hero |
|---|---|---|---|---|---|
| Label/eyebrow | 14 Semi Bold | 16 Semi Bold | 16 Semi Bold | 16 Semi Bold | 16 Semi Bold |
| Heading | 24 Medium | 28 Medium | 36 Semi Bold | 36 Semi Bold | 56 Semi Bold |
| Body | 18 Regular | 16 Regular | 24 Medium | 24 Medium | 24 Medium |

### Padding per tier

| | xs | sm-compact | sm | lg | hero |
|---|---|---|---|---|---|
| Inner padding | 24px | 24px | 48px | 48px | 48px |
| Label -> heading gap | 8px | 8px | 16px | 16px | 16px |
| Heading -> body gap | 12px | 12px | 16px | 16px | 16px |

### Slide-level text (outside cards)

| Element | Size | Weight | Color |
|---|---|---|---|
| Slide title | 48 | Semi Bold | Gray/900 #18181B |
| Slide body | 16 | Medium | Gray/700 #3F3F46 |
| Slide subtitle | 16 | Regular | Gray/500 #71717A |

**Title spacing rule:** The first element below a slide title must always be **64px** from the title's bottom edge. This applies to bento grids, timeline dots, horizontal lines, or any other content below the title.

Slide titles are always 48px. For giant statements, use `template-huge-fact` (Layer 3 territory).

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

**Rose scale:**

| Token | Hex |
|---|---|
| Rose/50 | #FFF1F2 |
| Rose/100 | #FFE4E6 |
| Rose/200 | #FECACA |
| Rose/300 | #FDA4AF |
| Rose/400 | #FF637E |
| Rose/500 | #F43F5E |
| Rose/600 | #EC003F |
| Rose/700 | #BE123C |
| Rose/800 | #A50036 |
| Rose/900 | #881337 |
| Rose/950 | #4D0218 |

**Green scale:**

| Token | Hex |
|---|---|
| Green/50 | #F0FCF5 |
| Green/100 | #DBFCE8 |
| Green/200 | #BAF7D1 |
| Green/300 | #87F0AB |
| Green/400 | #4ADE80 |
| Green/500 | #21C45E |
| Green/600 | #17A34A |
| Green/700 | #14803D |
| Green/800 | #176633 |
| Green/900 | #14542E |
| Green/950 | #052E17 |

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

**Rule:** Hide unused text elements (`visible = false`), never fill them with spaces.

---

## Layer 3: Impact Overrides

Impact typography is an **earned exception** to the card tier defaults. It triggers based on content, not card size. When content qualifies, swap the heading size for a higher typescale step. Everything else (label, body, padding) stays at the card tier default.

### Qualification rules

| Content type | Qualifies when | xs | sm | lg | hero |
|---|---|---|---|---|---|
| Single dramatic number | The number IS the message ("98%", "$2.1B") | 40 | 56 | 64 | 80 |
| Price/cost | Pricing is the focus of the card | 36 | 48 | 56 | 64 |
| Short punchy phrase | 3 words or fewer | 28 | 36 | 40 | 56 |
| Hero heading (short, <=4 chars) | The one dominant card, short number ("98%") | — | — | — | 80 |
| Hero heading (long, 5+ chars) | The one dominant card, longer text ("$2.1B") | — | — | — | 64 |

### What does NOT qualify

- Body copy — never override, stays at card tier default
- Labels/eyebrows — always at card tier default
- Headings when there are 5+ cards on a slide — scale **down**, don't scale up
- Multi-line headings (3+ lines) — not punchy enough for impact

### Standalone impact (no bento grid)

| Template type | Max heading size |
|---|---|
| `template-huge-fact` variants | 96 |
| `template-chapter-*` | 80 |

### Constraints

- **Maximum one impact element per card.**
- **Maximum one hero card per slide.**

---

## Grid System

All custom slides use a **6-unit column grid**:

```
Slide: 1920 x 1080px
Horizontal padding: 64px each side
Vertical padding: 80px top and bottom
Usable width: 1920 - 128 = 1792px
Unit width: (1792 - 5 x 32) / 6 = 272px
Gap between units: 32px
```

Common widths:
- 1 unit (272px) — xs tier
- 2 units (576px) — sm tier
- 3 units (880px) — lg tier
- 6 units (1792px) — full-width row

Row heights:
- 2 equal rows: (1080 - 160 - 32) / 2 = 444px each
- 3 equal rows: (1080 - 160 - 64) / 3 = 252px each
- Asymmetric: hero row taller, supporting rows shorter

**Named exception:** The timeline-bento template uses a 5-unit grid.

## Bento Card Construction

- **Corner radius:** 32px
- **Gap between cards:** 32px
- **Background:** Gray/100 (#F4F4F5) standard, Blue/600 (#2563EB) hero, Gray/900 (#18181B) dark/closing, White (#FFFFFF) on gray slide backgrounds
- **No drop shadows** (clean, flat aesthetic)
- **Clip content:** always true
- **Inner padding:** per card tier (see Layer 2)

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

1. **Does the content fit an existing template exactly?** -> Clone and fill.
2. **Does it fit but with fewer/more items?** -> Build from scratch using grid rules.
3. **What card tier does each cell fall into?** -> Look up Layer 2 for sizes and padding.
4. **Is there one number or fact that should dominate?** -> Check Layer 3 impact rules.
5. **Does every cell need body copy?** -> Probably not. Use minimum text combination.
6. **Is this a timeline?** -> Horizontal timeline (3-8 steps) or bento timeline.
7. **Is this a comparison?** -> Equal-width cells side by side.
8. **Is this pricing?** -> Pricing bento with impact numbers and hero hook cell.
