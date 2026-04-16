# Design System v2 — Layered Token System

## Problem

The current `templates/design-system.md` uses ranges for font sizes ("22-32px"), padding ("20-32px"), and hardcoded hex values that don't match the actual Figma design tokens. This leads to inconsistent output across presentation runs — slides in the same deck can look different because Claude picks different values from the ranges each time.

## Solution

Replace the current design system doc with a **three-layer token system**:

1. **Layer 1: Typescale** — a Minor Third scale defining every legal font size
2. **Layer 2: Card Size Tiers** — maps card width to exact typescale steps + padding + colors
3. **Layer 3: Impact Overrides** — content-triggered rules that swap heading sizes for larger steps

Each layer references the one below it. Claude reads bottom-up: "what card am I in?" -> tier -> defaults. "Does content qualify for impact?" -> override heading only.

---

## Layer 1: The Typescale

**Scale:** Minor Third (1.2 ratio), rounded to whole pixels.

```
12 · 14 · 16 · 18 · 20 · 24 · 28 · 32 · 36 · 40 · 48 · 56 · 64 · 80 · 96
```

Every font size in the system MUST come from this scale. No exceptions.

**Font:** Suisse Int'l
**Weights:** Semi Bold, Medium, Regular

### Line heights

Tighter as text gets larger. Three tiers:

| Size range | Multiplier | Rationale |
|---|---|---|
| 12-20px (body/labels) | size x 1.4 | Readable multi-line body copy needs air |
| 24-40px (headings) | size x 1.2 | Headings are short, tighter feels solid |
| 48px+ (display/impact) | size x 1.1 | Large text at tight leading looks intentional |

Full reference table:

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

Line heights rounded to nearest even number for clean pixel rendering.

---

## Layer 2: Card Size Tiers

Every bento card falls into one of four tiers based on its width. The tier determines the exact typescale steps and padding.

### Tier definitions

| Tier | Width | When |
|---|---|---|
| **xs** | <=272px (1 unit) | Single-unit cards, half-height cards |
| **sm** | 273-576px (2 units) | Standard cards, price cards |
| **lg** | 577-880px (3 units) | Wide cards, offer cards |
| **hero** | Any size, blue or dark bg | The one emphasized card per slide |

### Typography per tier

| Element | xs | sm | lg | hero |
|---|---|---|---|---|
| Label/eyebrow | 14 Semi Bold | 16 Semi Bold | 16 Semi Bold | 16 Semi Bold |
| Heading | 24 Medium | 28 Medium | 36 Semi Bold | 56 Semi Bold |
| Body | 14 Regular | 16 Regular | 18 Medium | 20 Medium |

### Padding per tier

| | xs | sm | lg | hero |
|---|---|---|---|---|
| Inner padding | 20px | 24px | 28px | 32px |
| Label -> heading gap | 8px | 8px | 8px | 12px |
| Heading -> body gap | 8px | 12px | 12px | 16px |

### Slide-level text (outside cards)

| Element | Size | Weight | Color |
|---|---|---|---|
| Slide title | 48 | Semi Bold | Gray/900 |
| Slide body | 16 | Medium | Gray/700 |
| Slide subtitle | 16 | Regular | Gray/500 |

Slide titles are always 48px. If a slide needs a giant statement, use a `template-huge-fact` (Layer 3 impact territory).

### Color system (design tokens)

Four scales from the Simple Design System library: Gray (50-950), Blue (50-950), Rose (50-950), Green (50-950).

#### Gray scale

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

#### Blue scale

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

#### Rose scale

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

#### Green scale

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

#### Presentation color roles

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

#### Color rules

- Rose and Green are **contextual** — only used when content is specifically about health or sustainability
- Blue is used sparingly: hero cards and accent dots only
- All other UI is grayscale

### Valid text combinations per cell

Not every cell needs all three text elements. Use the minimum needed:

1. **Heading only** — bold statement ("3 machines", "Entrance")
2. **Eyebrow + Heading** — labeled content ("Now" + "Order bottles")
3. **Heading + Body** — title with detail ("Entrance" + "Door wrap + floor trail stickers")
4. **Eyebrow + Heading + Body** — full stack ("Primary" + "Health-conscious" + "Read labels, research ingredients...")
5. **Body only** — rare, for footnotes or supporting context

**Rule:** Hide unused text elements (`visible = false`), never fill them with spaces.

---

## Layer 3: Impact Overrides

Impact typography is an **earned exception** to the card tier defaults. It triggers based on content, not card size. When content qualifies, swap the heading size for a higher step on the typescale. Everything else (label, body, padding) stays at the card tier default.

### Qualification rules

| Content type | Qualifies when | xs | sm | lg | hero |
|---|---|---|---|---|---|
| Single dramatic number | The number IS the message ("98%", "$2.1B") | 40 | 56 | 64 | 80 |
| Price/cost | Pricing is the focus of the card | 36 | 48 | 56 | 64 |
| Short punchy phrase | 3 words or fewer that carry the slide | 28 | 36 | 40 | 56 |
| Hero cell heading | The one dominant card per slide | — | — | — | 64-80 |

Hero impact size depends on character count: short numbers like "98%" get 80, longer like "$2.1B" get 64.

### What does NOT qualify

- Body copy — never override, stays at card tier default
- Labels/eyebrows — always at card tier default
- Headings when there are 5+ cards on a slide — scale **down**, don't scale up
- Multi-line headings (3+ lines) — if the text wraps that much, it's not punchy enough for impact

### Standalone impact (no bento grid)

Templates without cards where the content owns the entire slide:

| Template type | Max heading size |
|---|---|
| `template-huge-fact` variants | 96 |
| `template-chapter-*` | 80 |

### Constraints

- **Maximum one impact element per card.**
- **Maximum one hero card per slide.**
- This prevents the "everything is loud" problem.

---

## Sections carried forward (unchanged)

### Grid System

All custom slides use a **6-unit column grid**:

```
Slide: 1920 x 1080px
Horizontal padding: 64px each side
Vertical padding: 80px top and bottom
Usable width: 1920 - 128 = 1792px
Unit width: (1792 - 5 x 32) / 6 = 272px
Gap between units: 32px
```

A bento cell can span 1-6 units wide. Common widths:
- 1 unit (272px) — xs tier
- 2 units (576px) — sm tier
- 3 units (880px) — lg tier
- 6 units (1792px) — full-width row

Rows can be any height. Common patterns:
- 2 equal rows: (1080 - 160 - 32) / 2 = 444px each
- 3 equal rows: (1080 - 160 - 64) / 3 = 252px each
- Asymmetric: hero row taller, supporting rows shorter

**Named exception:** The timeline-bento template uses a 5-unit grid. This is the only template that deviates from the 6-unit standard.

### Bento Card Construction

- **Corner radius:** 32px
- **Gap between cards:** 32px
- **Background:** Gray/100 (#F4F4F5) for standard cards, Blue/600 (#2563EB) for hero, Gray/900 (#18181B) for dark/closing, White (#FFFFFF) for cards on gray slide backgrounds
- **No drop shadows** (clean, flat aesthetic)
- **Clip content:** always true
- **Inner padding:** determined by card tier (see Layer 2)

### Flexible Item Counts

Templates define a default number of items, but content may need more or fewer.

**Fewer items:** Hide unused cells (auto-layout) or build from scratch with fewer cells. Never fill empty cells with filler text.

**More items:** Build from scratch using the grid system. Maintain the same visual style.

| Items | Recommended layout | Grid pattern |
|---|---|---|
| 2 | 2 equal columns | 3u + 3u |
| 3 | 3 equal columns | 2u + 2u + 2u |
| 4 | 2x2 grid | (3u + 3u) x 2 rows |
| 5 | 2+3 or 3+2 rows | top: 2u+2u+2u, bottom: 3u+3u |
| 6 | 2x3 or 3x2 grid | (2u+2u+2u) x 2 rows |
| 7-8 | 4x2 grid | (varies) x 2 rows |

For timelines: 3-8 steps. Beyond 8, split across 2 slides.
For bento grids: 2-6 cells per slide. Beyond 6, content gets too small.

### Creative Decision Guide

When building a slide, follow this sequence:

1. **Does the content fit an existing template exactly?** -> Clone and fill.
2. **Does it fit but with fewer/more items?** -> Build from scratch using grid rules, matching the template's visual style.
3. **What card tier does each cell fall into?** -> Look up Layer 2 for exact sizes and padding.
4. **Is there one number or fact that should dominate?** -> Check Layer 3 impact qualification rules.
5. **Does every cell need body copy?** -> Probably not. Use the minimum text combination.
6. **Is this a timeline or sequential content?** -> Use horizontal timeline (3-8 steps) or bento timeline (with hero moment).
7. **Is this a comparison?** -> Use equal-width cells side by side.
8. **Is this pricing?** -> Use pricing bento with impact numbers and a hero hook cell.

---

## Migration notes

The existing Figma templates use hardcoded hex values that don't match the design tokens:
- `#0A84FF` in templates should become Blue/600 `#2563EB`
- `#1A1A1A` should become Gray/900 `#18181B`
- `#404040` should become Gray/700 `#3F3F46`
- `#777777` should become Gray/500 `#71717A`
- `#595959` should become Gray/600 `#52525B`
- `#F5F5F5` should become Gray/100 `#F4F4F5`
- `#219653` should become Green/600 `#17A34A`

These are close but not exact matches. Templates should be updated to use the correct token values.
