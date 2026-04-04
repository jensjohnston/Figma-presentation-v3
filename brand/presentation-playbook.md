# Presentation Design Playbook

This playbook captures the design language and decision patterns from reference presentations. Claude reads this during `/generate-presentation` to produce slides that match the quality and style of hand-crafted Bluewater decks.

## Scene Templates (Primary Approach)

**Always prefer scene templates over generic templates.** Scene templates are pre-composed visual scenes extracted from finished decks — they include product photography, gradient art, and visual compositions already baked in. The generator only swaps text, producing output that looks hand-crafted.

### How to use scenes:
- Check `sceneTemplates` in `registry.json` before falling back to generic `templates`
- When the user specifies a product (e.g., "flowater-pilates"), prefer that product's scenes
- **Free mixing is allowed** — a deck can pull scenes from different source decks
- When mixing, prefer scenes with compatible `visualTheme` values to avoid style clashes
- When using scenes, **never modify images or backgrounds** — `frozenVisuals: true` means the visual is final

### Growing the library:
- Use `/extract-scenes` to add new scene templates from any finished deck
- Each deck you hand-craft adds 8-12 new scenes to the library
- Over time, the library covers more products, audiences, and content patterns

## Reference: O™Pilates / Flowater Pilates Deck

Figma file `GkUiwJTK5Xi65AKw4MOjTL`, page "Flowater pilates 2" (node `53265:870`).

---

## 1. Overall Presentation Structure

A pitch deck follows this narrative arc:

| Position | Purpose | Typical slide type |
|----------|---------|-------------------|
| 1 | **Hook** — branded title slide with bold claim | Title with gradient mesh bg + dual logos |
| 2 | **Product reveal** — introduce the product visually | Product hero with images (bottle, ingredients) |
| 3 | **What's inside** — ingredients/features deep dive | Feature cards with colored/image backgrounds |
| 4 | **Differentiator** — competitive comparison | Bar chart or data visualization |
| 5 | **How it works** — the upgrade/integration story | Info slide with product machine photo |
| 6 | **Economics** — pricing/cost/margin | Pricing cards with product imagery |
| 7 | **Projections** — revenue scenarios | Scenario cards (conservative/moderate/strong) |
| 8-9 | **Customer experience** — how members buy | Product cards, refill options |
| 10 | **Getting started** — process steps | Bento cards with product/action photos |
| 11 | **Operations** — appendix/logistics | Clean bento cards with icons + bullet lists |
| 12 | **CTA** — closing call to action | Gradient bg with contact info |

---

## 2. The "Highlight Card" Pattern

**This is the most important design pattern.** When a slide has 2-3+ cards in a row, the **last card (or the "best" option)** gets special visual treatment:

- **Standard cards**: Light gray background (`#F4F4F5`), dark text
- **Highlight card**: Pink gradient mesh background with the brand flower/abstract art, white or pink text

### Examples from the reference:
- **Pricing slide**: "Your cost $0" (gray) | "Members pay $3.50" (gray + bottle photo) | "You keep $1" (pink gradient + flower art)
- **Projections slide**: "Conservative" (gray) | "Moderate" (gray) | "Strong" (pink gradient + flower art)
- **Process steps**: "1. Sign Up" (pink gradient) | "2. We Install" (product photo) | "3. Start selling" (product photo)

### When to apply:
- Revenue/economics slides → highlight the best scenario or the "you keep" card
- Pricing tiers → highlight the recommended option
- Process steps → the first step can get the gradient (it's the entry point)
- Feature comparisons → highlight the product's advantage

---

## 3. Product Photography Usage

**Every slide should incorporate product imagery where possible.** This is what makes the deck feel premium rather than generic.

### Image placement patterns:

| Slide type | Where images go |
|------------|----------------|
| Title/intro | Full-bleed gradient mesh background |
| Product reveal | 3-panel layout: ingredient closeup | bottle hero | ingredient closeup |
| Ingredient/feature cards | Each card has a relevant ingredient/nature photo blended behind the gradient bg |
| Pricing cards | Middle card has a product bottle photo; highlight card has brand art |
| Projections | Highlight card has brand flower art |
| Process steps | Each step card has a contextual photo (brand art, machine cap, tap cards) |
| Refill/purchase cards | Product bottle (single for 1-unit, arranged creatively for multi-unit) |
| Operations/appendix | Icon circles only — no product photos (keeps it clean/utilitarian) |

### Image sources:
- Use the `assets/library.json` to find product bottles, machine photos, ingredient closeups
- When generating images via AI (Gemini), request: "premium product photography, soft lighting, shallow depth of field, clean background"
- Brand gradient mesh / flower art is a recurring visual motif — use it on highlight cards and title slides

---

## 4. Ingredient / Feature Cards

When presenting product ingredients, features, or pillars:

### Card structure:
```
┌─────────────────────────────┐
│  [gradient bg + image]      │
│                             │
│  Ingredient Name            │  ← Bold, white, 32-36px
│  Metric (e.g. 150mg/500ml) │  ← Light, smaller
│                             │
│  Description paragraph      │  ← Medium weight, light color
│  explaining what it does    │
│  and why it matters.        │
│                             │
│  ─────────────────          │  ← Divider line
│  One-line benefit summary   │  ← Bottom of card
└─────────────────────────────┘
```

### Color-coding:
Each ingredient/feature card gets a unique color that relates to its nature:
- Green tones → natural/plant-based ingredients (L-theanine, electrolytes)
- Blue tones → energy/cognitive ingredients (Vitamin B12, minerals)
- Red/warm tones → sweetener/flavor components (Bluevi™, strawberry)
- Dark/neutral → general/technical features

### Important:
- Cards should have **image backgrounds** (ingredient closeups, nature textures) that show through the gradient
- The gradient overlays the image so text remains readable
- Each card should feel visually distinct through its color, not just its text

---

## 5. Pricing & Economics Slides

### Three-card economics layout:
```
[ Your cost: $X ]  [ Members pay: $X ]  [ You keep: $X ]
   (gray bg)         (gray + bottle)     (pink gradient)
```

- The "You keep" or "profit" card always gets the highlight treatment
- The middle card (what members pay) often includes a product bottle image
- Include a calculation basis footnote at the bottom

### Scenario projections:
```
[ Conservative ]  [ Moderate ]  [ Strong ]
   (gray bg)       (gray bg)    (pink gradient)
```

- Each card shows: scenario label, daily volume, Revenue + Gross Margin pair, time period
- The most optimistic scenario gets the highlight card treatment
- Include an annual cost footnote showing the investment pays for itself

---

## 6. Process / Getting Started Steps

Don't use abstract numbered circles. Use **bento-style cards** where each step card contains:
- A numbered heading: "1. Sign Up", "2. We Install", "3. Start selling"
- A short description paragraph
- A **contextual image** filling the bottom 60% of the card

Image choices for steps:
- Step 1 (Sign up/Start): Brand gradient art or abstract visual
- Step 2 (Install/Build): Close-up product detail photo (machine cap, module, hardware)
- Step 3 (Launch/Earn): Product-in-use photo (cards, bottles, the thing customers interact with)

---

## 7. Title & CTA Slides

### Title slide (first):
- Full-bleed pink gradient **mesh** background (organic, not linear gradient)
- Dual logo bar at top left (product logo + Flowater logo)
- Large bold white headline (2 lines max)
- Smaller white body text below

### CTA slide (last):
- Same pink gradient mesh background
- Centered headline with closing statement
- Body text with value prop summary
- Frosted glass CTA card with contact info

---

## 8. Color System

| Element | Color | Usage |
|---------|-------|-------|
| Background (standard) | White `#FFFFFF` | Most slides |
| Card background (standard) | Light gray `#F4F4F5` | Default card fill |
| Card background (highlight) | Pink gradient mesh | Featured/best-option cards |
| Title text | Near-black `#272729` | All slide titles |
| Body text | Dark gray `#71717A` | Descriptions, sublabels |
| Accent text | Pink `#E23957` | Eyebrows, highlighted values, "you keep" amounts |
| Card text (on dark/gradient) | White `#FFFFFF` | Text on colored or gradient cards |

### Pink gradient mesh:
The brand's signature visual is an organic gradient mesh using these tones:
- Deep pink: `#D1384D`
- Medium pink: `#E67380`
- Light pink: `#F2B3B8`
- Soft peach: `#F5D0D4`

This mesh appears on title slides, CTA slides, and highlight cards. It often includes the abstract flower/petal shapes.

---

## 9. Typography Hierarchy

All text uses **Suisse Int'l**.

| Element | Weight | Size | Notes |
|---------|--------|------|-------|
| Eyebrow | Medium | 30px | Sentence case, not uppercase in this style |
| Title | Semi Bold | 80px | One strong thought, period at end |
| Body | Medium | 30px | 2-3 lines max |
| Card heading | Semi Bold | 36px | Feature/ingredient name |
| Card metric | Medium | 20px | Quantitative detail |
| Card body | Medium | 22-24px | Description text |
| Large value | Semi Bold | 48-72px | Pricing numbers, stats |
| Footnote | Medium | 16-20px | Calculation basis, disclaimers |

---

## 10. Bar Chart / Comparison Slides

When comparing the product against competitors:
- Light background (not dark)
- Rounded rectangular bars in light gray
- Bars arranged by descending value, left to right
- The product (highlighted in brand pink/blue) is last, at the lowest/best value
- Large numbers above each bar
- Brand labels below

---

## 11. Adapting for Different Products

When generating a presentation for a new product (e.g., Opilatus, a different Flowater beverage):

1. **Swap the product-specific content** (ingredients, pricing, images) but keep the layout patterns
2. **Match the color palette** to the product — if the product is blue-themed, adjust card gradient colors accordingly while keeping the structure
3. **Use the same narrative arc** (hook → reveal → features → differentiator → economics → CTA)
4. **Source images** from the asset library that match the new product
5. **Preserve the highlight card pattern** — it works regardless of product
6. **Keep the same typography and spacing** — these are brand-level, not product-level decisions
