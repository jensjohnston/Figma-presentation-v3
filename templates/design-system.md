# Bluewater Design System

This document defines the rules for building presentation slides. Read this alongside `registry.json` when generating slides.

**When to use templates vs. build from scratch:**
- Content fits a template perfectly → clone and fill (fast)
- Content needs minor adaptation (hide a slot, skip body copy) → clone, fill, hide unused slots
- Content needs structural change (different item count, custom layout) → **build from scratch** using these rules

## Grid System

All custom slides use a **6-unit column grid**:

```
Slide: 1920 × 1080px
Horizontal padding: 64px each side
Vertical padding: 80px top and bottom
Usable width: 1920 - 128 = 1792px
Unit width: (1792 - 5 × 32) / 6 ≈ 272px
Gap between units: 32px
```

A bento cell can span 1-6 units wide. Common widths:
- 1 unit (272px) — small card, single stat or label
- 2 units (576px) — standard card, title + body
- 3 units (880px) — wide card, hero content
- 6 units (1792px) — full-width row

Rows can be any height. Common patterns:
- 2 equal rows: (1080 - 160 - 32) / 2 = 444px each
- 3 equal rows: (1080 - 160 - 64) / 3 = 252px each
- Asymmetric: hero row taller, supporting rows shorter

## Bento Card Construction

Every bento card follows these rules:
- **Corner radius:** 32px
- **Gap between cards:** 32px
- **Background:** #F5F5F5 (light gray) for standard, #0A84FF (blue) for hero/accent, #1E1E1E (dark) for closing/contrast, white for cards on gray slide backgrounds
- **No drop shadows** on bento cards (clean, flat aesthetic)
- **Clip content:** always true

### Text inside bento cards

Padding from card edges: 20-32px (scale with card size — 20px for small 1-unit cards, 28-32px for larger cards).

## Typography

Font: **Suisse Int'l** (Semi Bold, Medium, Regular)

### Slide-level text

| Element | Weight | Size | Color | Notes |
|---------|--------|------|-------|-------|
| Title | Semi Bold | 48-80px | #1A1A1A | 80px for statement slides, 48px for content slides |
| Body/subtitle | Regular | 16-20px | #777777 | Below title, optional — hide if not needed |

### Inside bento cells

| Element | Slot name pattern | Weight | Size | Color | When to use |
|---------|-------------------|--------|------|-------|-------------|
| Eyebrow | `*-label-N` | Semi Bold | 13-16px | #404040 | Date, category, tag, number. No letter-spacing. |
| Heading | `*-heading-N` | Semi Bold | 22-32px | #1A1A1A | Primary content. The main thing the card communicates. |
| Body | `*-body-N` | Regular or Medium | 14-17px | #777777 | Supporting detail. Use Medium weight for slight emphasis. |

### Spacing between text elements inside cells

- Eyebrow to heading: **8px**
- Heading to body: **12px**
- Footnote/deadline: anchored **20-32px from bottom** of cell

### Valid text combinations per cell

Not every cell needs all three text elements. Use the minimum needed:

1. **Heading only** — bold statement ("3 machines", "Entrance")
2. **Eyebrow + Heading** — labeled content ("Now" + "Order bottles")
3. **Heading + Body** — title with detail ("Entrance" + "Door wrap + floor trail stickers")
4. **Eyebrow + Heading + Body** — full stack ("Primary" + "Health-conscious" + "Read labels, research ingredients...")
5. **Body only** — rare, for footnotes or supporting context

**Rule:** Hide unused text elements (`visible = false`), never fill them with spaces.

## Impact Typography — When to Break the Rules

Sometimes content demands bigger, bolder treatment. These are **earned exceptions**, not defaults:

### When to scale up

| Content type | Default size | Impact size | When to use impact |
|-------------|-------------|-------------|-------------------|
| Single dramatic number | 22-32px | 56-140px | The number IS the message ("98%", "3,200+", "~100") |
| Price/cost | 22-32px | 48-80px | Pricing is the focus of the card |
| Short punchy phrase | 22-32px | 36-56px | 3 words or fewer that carry the slide ("Machines go live.") |
| Hero cell heading | 32px | 64-80px | Blue/dark hero cells — the one thing you read first |

### When NOT to scale up

- Body copy — never larger than 20px, even for emphasis
- Eyebrows — always 13-16px, they're labels not headlines
- When there are many items on the slide — scale down, don't compete

### The "hero cell" pattern

One cell per slide can be the **hero** — larger, colored (blue or dark), with scaled-up typography. Use this for:
- The most important number or fact
- A call to action
- The climactic moment in a timeline
- A promotional hook

Hero cells are typically 2-3 units wide and use white text on blue (#0A84FF) or dark (#1E1E1E) backgrounds.

## Color System

| Color | Hex | Usage |
|-------|-----|-------|
| Gray 900 | #1A1A1A | Headings, primary text |
| Gray 700 | #404040 | Eyebrows, labels |
| Gray 500 | #777777 | Body copy, supporting text |
| Gray 200 | #F5F5F5 | Bento card backgrounds |
| White | #FFFFFF | Slide background, text on dark/blue |
| Blue | #0A84FF | Hero cells, accent dots, progress indicators |
| Dark | #1E1E1E | Contrast cards, closing/final items |
| Green 600 | #219653 | Positive badges ("Save 34%") |

## Flexible Item Counts

Templates define a default number of items, but content may need more or fewer. Rules:

### Fewer items than the template
- **Hide unused cells** if the template is auto-layout
- **Or build from scratch** with fewer cells using the grid system
- Never fill empty cells with filler text

### More items than the template
- **Build from scratch** using the grid system
- Maintain the same visual style (card bg, typography, spacing)
- For timelines: 3-8 steps work well. Beyond 8, consider splitting across 2 slides.
- For bento grids: 2-6 cells per slide. Beyond 6, content gets too small.

### How to decide the grid for N items

| Items | Recommended layout | Grid pattern |
|-------|-------------------|--------------|
| 2 | 2 equal columns | 3u + 3u |
| 3 | 3 equal columns | 2u + 2u + 2u |
| 4 | 2×2 grid | (3u + 3u) × 2 rows |
| 5 | 2+3 or 3+2 rows | top: 2u+2u+2u, bottom: 3u+3u |
| 6 | 2×3 or 3×2 grid | (2u+2u+2u) × 2 rows |
| 7-8 | 4×2 grid | (varies) × 2 rows |

For asymmetric layouts (hero cell + smaller cells), allocate 2-3 units to the hero and distribute remaining items in 1-unit cells around it.

## Creative Decision Guide

When building a slide, ask these questions:

1. **Does the content fit an existing template exactly?** → Clone and fill.
2. **Does it fit but with fewer/more items?** → Build from scratch using grid rules, matching the template's visual style.
3. **Is there one number or fact that should dominate?** → Use impact typography. Consider a hero cell.
4. **Does every cell need body copy?** → Probably not. Use the minimum text combination that communicates clearly.
5. **Is this a timeline or sequential content?** → Use horizontal timeline (3-8 steps) or bento timeline (with hero moment).
6. **Is this a comparison?** → Use equal-width cells side by side.
7. **Is this pricing?** → Use pricing bento with impact numbers and a promotional hero cell.
