# Design System v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the range-based design system doc with a three-layer token system (typescale, card tiers, impact overrides) for consistent slide output.

**Architecture:** Single file rewrite of `templates/design-system.md` plus alignment updates to `templates/registry.json` (typography section) and `CLAUDE.md`. No code, no build step — these are configuration/documentation files that Claude reads at generation time.

**Tech Stack:** Markdown, JSON

---

### Task 1: Rewrite `templates/design-system.md` with the layered system

**Files:**
- Modify: `templates/design-system.md` (full rewrite)

- [ ] **Step 1: Replace the entire contents of `templates/design-system.md`**

Write this exact content:

```markdown
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

Every bento card falls into one of four tiers based on its width.

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
| Slide title | 48 | Semi Bold | Gray/900 #18181B |
| Slide body | 16 | Medium | Gray/700 #3F3F46 |
| Slide subtitle | 16 | Regular | Gray/500 #71717A |

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
| Hero cell heading | The one dominant card | — | — | — | 64-80 |

Hero impact size depends on character count: short numbers like "98%" get 80, longer like "$2.1B" get 64.

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
```

- [ ] **Step 2: Verify the file is well-formed**

Open `templates/design-system.md` and verify:
- All markdown tables render correctly
- The typescale line reads: `12 · 14 · 16 · 18 · 20 · 24 · 28 · 32 · 36 · 40 · 48 · 56 · 64 · 80 · 96`
- All hex colors use uppercase 6-digit format
- No ranges remain (no "22-32px", "20-32px", "48-80px", etc.)

- [ ] **Step 3: Commit**

```bash
git add templates/design-system.md
git commit -m "Rewrite design-system.md with layered token system (typescale, card tiers, impact overrides)"
```

---

### Task 2: Update `templates/registry.json` typography section

**Files:**
- Modify: `templates/registry.json:8-37` (the `typography` block)

The registry has a top-level `typography` object that currently contains ranges and old hex values. Update it to match the new layered system.

- [ ] **Step 1: Replace the `typography` block in `registry.json`**

Replace the entire `"typography": { ... }` block (lines 8-37) with:

```json
"typography": {
  "fontFamily": "Suisse Int'l",
  "weights": ["Semi Bold", "Medium", "Regular"],
  "typescale": [12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 64, 80, 96],
  "lineHeightRules": {
    "body (12-20px)": "size x 1.4",
    "heading (24-40px)": "size x 1.2",
    "display (48px+)": "size x 1.1"
  },
  "cardTiers": {
    "xs": {
      "maxWidth": 272,
      "label": { "size": 14, "weight": "Semi Bold", "color": "#3F3F46" },
      "heading": { "size": 24, "weight": "Medium", "color": "#18181B" },
      "body": { "size": 14, "weight": "Regular", "color": "#71717A" },
      "padding": 20,
      "labelHeadingGap": 8,
      "headingBodyGap": 8
    },
    "sm": {
      "maxWidth": 576,
      "label": { "size": 16, "weight": "Semi Bold", "color": "#3F3F46" },
      "heading": { "size": 28, "weight": "Medium", "color": "#18181B" },
      "body": { "size": 16, "weight": "Regular", "color": "#71717A" },
      "padding": 24,
      "labelHeadingGap": 8,
      "headingBodyGap": 12
    },
    "lg": {
      "maxWidth": 880,
      "label": { "size": 16, "weight": "Semi Bold", "color": "#3F3F46" },
      "heading": { "size": 36, "weight": "Semi Bold", "color": "#18181B" },
      "body": { "size": 18, "weight": "Medium", "color": "#71717A" },
      "padding": 28,
      "labelHeadingGap": 8,
      "headingBodyGap": 12
    },
    "hero": {
      "label": { "size": 16, "weight": "Semi Bold", "color": "#FFFFFF" },
      "heading": { "size": 56, "weight": "Semi Bold", "color": "#FFFFFF" },
      "body": { "size": 20, "weight": "Medium", "color": "#FFFFFF" },
      "padding": 32,
      "labelHeadingGap": 12,
      "headingBodyGap": 16
    }
  },
  "slideLevel": {
    "title": { "size": 48, "weight": "Semi Bold", "color": "#18181B" },
    "body": { "size": 16, "weight": "Medium", "color": "#3F3F46" },
    "subtitle": { "size": 16, "weight": "Regular", "color": "#71717A" }
  },
  "impact": {
    "dramaticNumber": { "xs": 40, "sm": 56, "lg": 64, "hero": 80 },
    "price": { "xs": 36, "sm": 48, "lg": 56, "hero": 64 },
    "punchyPhrase": { "xs": 28, "sm": 36, "lg": 40, "hero": 56 },
    "standalone": { "hugeFact": 96, "chapter": 80 }
  },
  "colors": {
    "gray": {
      "white": "#FFFFFF", "50": "#FAFAFA", "100": "#F4F4F5", "200": "#E4E4E7",
      "300": "#D4D4D8", "400": "#A1A1AA", "500": "#71717A", "600": "#52525B",
      "700": "#3F3F46", "800": "#27272A", "900": "#18181B", "950": "#09090B"
    },
    "blue": {
      "50": "#F0F5FF", "100": "#DBEAFE", "200": "#BFDBFE", "300": "#93C5FD",
      "400": "#60A5FA", "500": "#3B82F6", "600": "#2563EB", "700": "#1D4ED8",
      "800": "#1E40AF", "900": "#153E88", "950": "#00205B"
    },
    "rose": {
      "50": "#FFF1F2", "100": "#FFE4E6", "200": "#FECACA", "300": "#FDA4AF",
      "400": "#FF637E", "500": "#F43F5E", "600": "#EC003F", "700": "#BE123C",
      "800": "#A50036", "900": "#881337", "950": "#4D0218"
    },
    "green": {
      "50": "#F0FCF5", "100": "#DBFCE8", "200": "#BAF7D1", "300": "#87F0AB",
      "400": "#4ADE80", "500": "#21C45E", "600": "#17A34A", "700": "#14803D",
      "800": "#176633", "900": "#14542E", "950": "#052E17"
    }
  },
  "bentoGrid": {
    "cornerRadius": 32,
    "gap": 32,
    "slidePaddingHorizontal": 64,
    "slidePaddingVertical": 80,
    "cardBg": "#F4F4F5",
    "heroBg": "#2563EB",
    "darkBg": "#18181B"
  }
}
```

- [ ] **Step 2: Validate JSON**

Run: `python3 -c "import json; json.load(open('templates/registry.json')); print('Valid JSON')"`

Expected: `Valid JSON`

- [ ] **Step 3: Commit**

```bash
git add templates/registry.json
git commit -m "Update registry.json typography to match layered design system v2"
```

---

### Task 3: Update CLAUDE.md references

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update the Design System section in CLAUDE.md**

Find this block:

```markdown
## Design System

- `templates/design-system.md` — Grid construction, typography (including impact rules), bento card rules, color system, creative decision guide
```

Replace with:

```markdown
## Design System

- `templates/design-system.md` — Three-layer token system: typescale (Minor Third), card size tiers (xs/sm/lg/hero with fixed sizes), impact overrides (content-triggered exceptions). Also covers grid, bento cards, colors (Gray/Blue/Rose/Green token scales), and creative decision guide.
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "Update CLAUDE.md to describe layered design system structure"
```

---

### Task 4: Verify the generate-presentation command reads the new structure

**Files:**
- Read: `.claude/commands/generate-presentation.md`

- [ ] **Step 1: Read the generate-presentation command**

Read `.claude/commands/generate-presentation.md` and check how it references `design-system.md`. Verify it says something like "Read templates/registry.json and templates/design-system.md". If it references specific sections by name (e.g., "## Typography"), update those references to match the new section names (e.g., "## Layer 1: The Typescale", "## Layer 2: Card Size Tiers").

- [ ] **Step 2: If changes needed, update and commit**

```bash
git add .claude/commands/generate-presentation.md
git commit -m "Update generate-presentation references to new design system sections"
```

If no changes needed, skip this step.
