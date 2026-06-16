# Generate Figma Presentation from PDF

Convert a PDF presentation into an on-brand Bluewater Figma deck using pre-made templates.

## Usage
```
/generate-presentation <path-to-pdf>
```

The user provides a path to a PDF file. You will read it, analyze each slide, match it to the best Bluewater template, and generate the full presentation in Figma.

## Important: Load the figma-use skill

Before calling any `use_figma` MCP tool, you MUST invoke the `figma:figma-use` skill. This is mandatory for every session.

## Step 1: Read the Template Registry AND Design System

Read both files from the project root:

### `templates/registry.json`
- `fileKey`: The Figma file key (`GkUiwJTK5Xi65AKw4MOjTL`)
- `templatePageId`: The canonical template page — **Template references** (`56881:463`)
- `typography`: The typography system (font sizes, weights, colors, spacing rules)
- `templates`: All templates with their slots, matchHints, and `flexible` metadata

### `templates/design-system.md`
- Three-layer token system: Layer 1 (typescale), Layer 2 (card size tiers with fixed font sizes and padding), Layer 3 (impact overrides)
- Grid construction rules (6-unit column grid, 32px gaps, 64/80px padding)
- Bento card construction (radius, colors, text placement)
- Color token scales (Gray, Blue, Rose, Green — each 50-950)
- Flexible item count rules and creative decision guide

**You have creative freedom.** Templates are shortcuts for common patterns, but you can build custom layouts from the design system rules when content doesn't fit a template. The design system is your primary reference — templates are secondary.

This contains:
- `templates`: A map of all 41 templates with their `nodeId`, `category`, `description`, `slots`, and `matchHints`

You will use this registry throughout the process.

### `industries/registry.json` (industry logo gardens)

Also read `industries/registry.json`. This holds **industry-specific logo garden slides** — finished, cloneable Figma frames for hospitality, gym/fitness, golf/sport, tech, media, and a general mix. Keyed by industry slug with `aliases`, `matchHints`, `nodeId`, and `defaultTitle`.

### `products/registry.json` (product packs)

Also read `products/registry.json`. This is the **product-aware** layer: finished,
on-brand, hand-built product slides the team is happy with (e.g. Kitchen Station, the
purifier range), each indexed as a **product pack**:
- `products.<slug>.aliases` — detection terms (used in Step 2 to decide which products a deck is about)
- `products.<slug>.slides[]` — finished slides with `role`, `nodeId`, `frameName`, `matchHints`, and `slots` (the editable text the generator rewrites)
- `products.<slug>.content` — verified `valueProps` / `keySpecs` / `components` to fill thin slides
- `products.<slug>.images[]` — `assetKey` references into `assets/library.json`

These are **finished shells**: when a product slide fits an incoming slide, you **clone it and
rewrite only the text** (Step 4 product-first rule). This is purely additive — if no product is
detected or none fits, the pipeline behaves exactly as before (from-scratch with generic templates).

### `brand/trademarks.json` (trademark dictionary)

Also read `brand/trademarks.json`. This holds:
- `terms[]` — brand/product names that trigger a ™ or ® node (e.g. `Café Station` → `™`, `Liquid Rock` → `®`)
- `titleSuperscriptSpec` — rendering spec: `fontFamily` (Suisse Int'l), `fontStyle` (Regular), `sizeRatio` (0.25 = 25% of title size), `gapPx` (0px — flush after the glyph edge)

You will use it in Step 5b after setting the `title` slot — call `placeTrademarkSuperscript(slide, titleNode, trademarks)` (defined in §5b). It is a no-op when no term in the dictionary matches the title text.

## Step 2: Read the Source PDF

Use the Read tool to read the PDF file provided by the user. Claude can read PDFs natively.

For each page/slide in the PDF, extract:
1. **Title text** — the main heading
2. **Body/subtitle text** — supporting text below the title
3. **Bullet points** — list items (note headings vs descriptions if present)
4. **Data/numbers** — key metrics, percentages, stats
5. **Quotes** — testimonial text with attributions
6. **Table data** — rows and columns of structured data
7. **Visual layout hints** — is it a comparison? A grid? A single statement?

Build a structured manifest of all slides before proceeding.

### Detect products (additive)

After building the slide manifest, **scan the deck's full text** (all extracted titles, bodies,
bullets) against every `products.<slug>.aliases` list in `products/registry.json`. Record the set
of **matched product slugs** (zero, one, or several). For each matched product, load its pack
(slides + content + images) — you will prefer it during matching (Step 4) and filling (Step 5).

If **no** product matches, skip the product-first path entirely and proceed exactly as today.

### Detect industries (additive)

Also scan the deck's full text against every `industries.<slug>.aliases` list in `industries/registry.json`. Record the **matched industry slug** (at most one — pick the strongest match by alias overlap; ties go to `general`). You will use it in Step 4 to route logo garden slides to the right industry frame instead of the generic `template-logo-garden-3x3`.

## Step 3: Presentation Preferences

Before matching templates, ask the user two questions using AskUserQuestion. These choices shape how you handle content in all subsequent steps.

### Question 1: Content Length

Ask: **"How should I handle the text content from your PDF?"**

Options:
- **Keep original text** — Use the exact text from the PDF. Only trim if it physically won't fit a template slot. This is the default.
- **Condense** — Rewrite text to be shorter and punchier. Reduce bullet points, tighten headlines, cut filler. Aim for ~60% of original length.
- **Expand** — Flesh out thin slides with more detail. Add context, supporting points, or fuller descriptions where the original is sparse.

### Question 2: Voice & Tone

Ask: **"What voice should the presentation use?"**

Options:
- **Keep original voice** — Preserve the tone, style, and language of the source PDF as-is.
- **Bluewater brand voice** — Rewrite all text in the Bluewater brand voice. (See `brand/voice-guide.md` if it exists in the project. If it doesn't exist yet, use a clean, confident, premium-but-approachable tone — short sentences, active voice, no jargon, focus on outcomes over features.)

### Question 3: Review mode

Ask: **"How do you want to review the deck?"**

Options:
- **Curated** — For ambiguous slides I render up to 3 layout alternatives you pick from; then every image slide gets an alternates strip for quick swaps before we finalize. This is the default.
- **Direct** — One-shot build, no review rounds (the previous behavior). For quick throwaway decks.

In Direct mode, skip Step 4.5, Step 5.5 and Step 5.6 entirely.

### How to apply these choices

- **Keep original + Keep voice**: Slot text in verbatim. Only adapt when content doesn't fit a template (e.g., too many bullets → condense to fit the template's slot count).
- **Keep original + Bluewater voice**: Rewrite for tone while keeping the same information and length.
- **Condense + Keep voice**: Shorten text while preserving the original style.
- **Condense + Bluewater voice**: Shorten AND rewrite in brand voice — most transformation.
- **Expand + Keep voice**: Add detail in the original author's style.
- **Expand + Bluewater voice**: Add detail in the Bluewater brand voice.

Carry the user's choices forward into Steps 4 and 5. When presenting the slide plan, note any slides where content was adapted and why.

## Step 4: Match Each Slide to a Template

For each extracted slide, select the best template from the registry using these rules (in priority order):

### Product-first (check BEFORE template matching)

If one or more products were detected in Step 2, check the product pack(s) **before** reaching for
a generic template:

- If a matched product has a slide whose **`role` + `matchHints` fit this incoming slide's intent**,
  **clone that finished product slide and rewrite only its text slots** from the incoming PDF
  (apply the Step 3 length/voice choices to the rewrite). Where the PDF is thin, fill from the
  product's `content` block (`valueProps` / `keySpecs` / `components`) rather than inventing facts.
  Then place any referenced product `images` (by `assetKey` → `assets/library.json`).
- Role gives the coarse filter (does the deck's intent map to a role the product has?), `matchHints`
  resolves the fine call. **Ties resolve toward reusing the product slide** — it is already on-brand and approved.
- Only if **no** product slide fits this slide → fall through to the generic Matching Priority below
  (today's behavior), but still **prefer the product's `content` + `images`** when filling those generic templates.

Product slides are finished shells — see Step 5b "Cloning a product slide" for the build pattern.
This path is skipped entirely when no product was detected.

### Matching Priority

All templates live on the **"Template references"** page (`56881:463`, status `primary`). The **"Templates 4"** page (`50285:14832`) is `retired` / `routable: false` — never clone from it. Every `registry.json → templates` entry has `page: "Template references"` and `status: KEEP`; walk the priority list below to pick the best shape.

1. **First slide** → opening title:
   - With imagery → `cover-with-product` (Template references)
   - Title + subtitle, no imagery → `template-title-subtitle-center` or `template-title-subtitle-left` (KEEP)
   - Title only → `template-title-center` or `template-title-left` (KEEP)
2. **Closing / CTA slide** → `closing-pure-title` (Template references — large centered title at y=400 with CTAs and contact)
3. **Section divider (1–5 word heading)** → `template-chapter-left`, `-center`, or `-right` (KEEP)
4. **Single dramatic visual statement (chapter divider with imagery)** → `full-bleed-hero` (Template references — image fills slide, title overlay bottom-left)
5. **Tech / feature hero with full-bleed atmospheric image** → `full-bleed-tech-hero` (Template references)
6. **One dominant idea + 3 supporting points** → `pentagrid-right` (Template references — 1 hero card right + 3 stacked left)
7. **2–4 distinct items of equal weight, image-rich** → `pillar-grid-4up-image` or `pillar-grid-3up-product` (Template references). Use `-with-body` variant when items need fuller copy. `pillar-grid-3up-functional` for product-functional pattern.
8. **Pricing tiers with rent/buy/add-ons** → `pillar-grid-3up-pricing` (Template references). Fall back to `template-pricing-bento` (OVERLAP) if structure doesn't match.
9. **Person/place/testimonial split** → `split-portrait` (Template references — 50/50 text + photo). Variant: `split-portrait-product-family` for "title left + 4 product list right".
10. **4–6 mixed items with one hero visual** → `bento-mix-center-hero` (Template references)
11. **Variety/flavor showcase, 7+ small image cards** → `pillar-grid-large-image` (Template references)
12. **3-column bento with image + dense per-cell copy** → `bento-3up-delivery` (Template references)
13. **Single dramatic number alone** → `template-huge-fact`, `template-huge-fact-eyebrow`, or `template-huge-fact-body` (KEEP)
14. **2–4 metrics in a row** → `template-metrics-4` (KEEP)
15. **Quote with attribution** → `template-quote1-middle` or `template-quote2-middle` (KEEP)
16. **Numbered process/steps** → `numbered-list` (Template references)
17. **Tabular data** → `template-table-2columns`, `-3columns`, `-4columns` (KEEP, by column count)
18. **Logos / social proof** → check `industries/registry.json` first:
    - If a slide's intent matches `matchHints` in any industry entry AND a matching industry was detected in Step 2, **clone that industry's logo garden frame** (same clone-move pattern as product slides; rewrite only the `title` slot using the `defaultTitle` or the PDF's slide title adapted to Bluewater voice; `meta-left` = deck label; no `meta-right` needed — the cloned frame omits it). Audit with `kind: "skip"`.
    - No industry match → fall back to `template-logo-garden-3x3` (KEEP).
19. **Side-by-side comparison** → `template-comparison-50-50` (OVERLAP)
20. **Timeline / roadmap** → `template-timeline-bento`, `-timeline-cards`, or `-timeline-horizontal` (OVERLAP)
21. **Generic 2–6 bento (no clear hero, no imagery available)** → `template-bento2`/`-bento3`/`-bento4`/`-bento5`/`-bento6`, or asymmetric `template-bento-25-75` / `-33-66` / `-66-33` / `-75-25` (OVERLAP)
22. **Title + 2-4 supporting bullets** → `template-info-2bullets`, `-3bullets`, or `-4bullets` (OVERLAP)
23. **Title + paragraph + image** → `template-info-left-middle`, `-info-left-top`, `-info-left-bottom`, `-info-center-center`, `-info-split-top` (OVERLAP)
24. **Product showcase, 2–3 products without pricing** → `template-product-2` or `template-product-3` (OVERLAP)
25. **Checklist** → `template-checklist-bento` (OVERLAP)
26. **Anything that fits no template above** → **CREATIVE ESCAPE HATCH** (build from scratch — see Creative Decision Rules)

**Bullet templates (`template-bullets-4/6/8`, `template-technical-bullets`)** were harmonized and restored to the references page on 2026-05-29 (status `KEEP`): clean text-bullet grids with heading + body per item (4-up/6-up = 36px headings, 8-up = 28px, technical = 20px spec rows + a left image area). Prefer image-rich `pillar-grid-*` / `bento*` when the content suits imagery; reach for the bullet grids when you want a clean text-only list of headed points.

**Preference tie-breaker:** before finalizing each slide's template, check `assets/preferences.json → templatePicks` for records with a similar `contentShape`. A template repeatedly chosen (≥2) for similar content wins ties and close calls; one repeatedly rejected is demoted below its rivals. Preferences never override the structural rules above (item counts, content types) — they only settle close calls. In Curated mode this also reorders which 3 candidates become the A/B/C alternatives (most-preferred = A).

### Creative Decision Rules

Before finalizing template selection, apply these judgment calls:

**Every template lives on Template references — one canonical source.** As of 2026-05-29 all generator templates were harmonized and consolidated onto the **Template references** page; the **Templates 4** page is `retired` / `routable: false` (kept for history only). Never route to or clone from Templates 4. Every entry in `registry.json → templates` already points at a harmonized references frame, so a clone is on-spec by construction: clone → set text → done, no geometry post-processing.

**Image-rich is better than text-only.** When a slide has 2–4 distinct items, prefer `pillar-grid-*` (image cards on top) over `template-bento*` (text-only). If no asset matches, the image cards render with FIG placeholders — visually clear that imagery is missing.

**Use impact typography** when a slide has a dramatic number, percentage, or short punchy phrase. Look up the impact size from `design-system.md` Layer 3 based on the card tier. This overrides the default heading size.

**Skip body copy** when headings alone communicate the point. Templates with `optionalSlots: ["body"]` (most pillar-grid variants) support this — hide the body slot per item with `visible = false`.

**Creative mix directive (decks ≥6 content slides):** Vary patterns. No more than **3 of any single pattern in a row**, no more than **60% of content slides** in any one pattern. Tables, quotes, and chapter dividers count toward variety.

**Build from scratch (escape hatch)** when:
- The slide content fits NO template above, even loosely.
- Item count exceeds what any template supports (e.g., 9 distinct items).
- Content has a unique constraint (e.g., a custom diagram, a one-off pricing comparison).

When using the escape hatch, follow the **Creative escape hatch** section in `templates/design-system.md`:
- Always call `applyChrome(slide, { metaLeftText, metaRightText, titleText, isDark })` first.
- Always run `auditChrome(slide)` before returning. Issues array must be empty.
- Use only typescale Layer 1 sizes; only Gray/Blue/Rose/Green tokens; only 32px gap and corner radius; only 48px outer margins.
- Draw layout inspiration from frames on the Template references page (id `56881:463`) — pick the closest pattern and adapt.
- Document the deviation in the slide frame's name (e.g., `Slide 12 — Custom · 7 cells`).

### Content Adaptation Rules
Apply the user's choices from Step 3 when filling content:
- **Titles end with a period** (brand rule): every slide `title`/headline ends in a full stop — unless it already ends in terminal punctuation (`?`/`!`). Add the dot when filling or cloning. Does not apply to eyebrows, subtitles, body, labels, or meta. See `design-system.md` → "Titles end with a period."
- **Content length**: If "Keep original", use verbatim text. If "Condense", rewrite shorter. If "Expand", add detail.
- **Voice**: If "Keep original", preserve the source tone. If "Bluewater brand voice", rewrite in brand voice (or use `brand/voice-guide.md` if available).
- If text is too long for a slot regardless of length choice, rewrite it more concisely while preserving meaning
- For table templates, if the source has more rows than the template supports (6 rows), summarize or truncate to fit

### Flexible Templates & Building from Scratch
- Check the template's `flexible` field in the registry. If it has `buildFromScratch: true`, you can build a custom version with a different item count using the design system rules.
- **Optional slots**: Check the `optionalSlots` array. Hide these with `visible = false` when the content doesn't need them. Never fill unused slots with spaces or filler.
- **Re-anchor after hiding (REQUIRED):** template containers are auto-layout frames that **hug** their content. Hiding a slot shrinks the frame but leaves it pinned at its original top `y`, floating the rest mid-region. After hiding any slot, re-anchor each bottom-justified block so its bottom edge returns to position: slide-level block → `block.y = 1032 - block.height`; in-card block → `block.y = (cardHeight - 48) - block.height` (read `block.height` AFTER hiding). See `design-system.md` → "Bottom-anchor rule". This bit slides 8/12/15/18/26 in the first Beam build — split-portrait body and comparison-3up stat blocks floated mid-slide until re-anchored.
- **Impact slots**: Check the `impactSlots` array. When content in these slots is a dramatic number, percentage, or short punchy phrase (3 words or fewer), look up the impact size from `design-system.md` Layer 3 based on the card tier.
- **Item count mismatch**: If a slide has 6 items but the best template has 5, build a custom version from scratch using the 6-unit grid system. Do NOT leave empty cells or cram content.
- **Bento preference**: For any set of 2-6 distinct items (features, phases, risks, locations), prefer bento grids over bullet lists. They're more visually engaging.

### Present the Slide Plan
Before generating anything in Figma, present the full slide plan to the user:

```
Slide Plan:
1. [template-title-subtitle-center] "Company Overview" — Title slide with subtitle
2. [template-chapter-left] "Our Mission" — Chapter divider
3. [template-bullets-4] "Key Products" — 4 product highlights
...
```

Ask the user to confirm before proceeding. They can request changes to template selections.

In **Curated mode**, the plan confirmation is lightweight (the real review happens on rendered slides in Step 4.5) — present the plan, apply any corrections, and continue without a blocking confirm.

## Step 4.5: Layout pass (Curated mode only)

The curator judges finished, rendered slides — never template names.

1. **Variant count per slide (adaptive):** while matching in Step 4, score the top template candidates 1–10 for fit. A slide is **ambiguous** when the top two scores are within 2 points → build the top **3** candidates as alternatives. One clear answer → 1 variant. Always 1 variant for: covers, chapter dividers, closing slides, and product-pack clones (already-approved layouts). To generate candidates, walk the Step 4 priority list past the first match and take the next 2 templates that could also hold the content (same item count or compatible layout category) — those are B and C. Rubric: 10 = exact structural match; 7–9 = strong fit, minor compromises; 4–6 = workable but less ideal; 1–3 = stretch. Score all candidates before deciding ambiguity.
2. **Build the review grid:** build every variant as a complete slide (full §5 build — text, images per §5d, chrome, audit). Position: slide i at x = i·2120; variant A (the recommendation) at y = 0, B at y = 1280, C at y = 2560. Frame names: `S04-A — pillar-grid-4up-image (recommended)`, `S04-B — template-bento4`, … For review-grid variant builds, treat `auditSlide` issues as warnings (append them to the variant's frame name, e.g. `S04-B — template-bento4 ⚠ title-size`) — the §5g STOP rule applies only to the assembled final deck. Report surviving variant audit issues after picks are confirmed.
3. **Collect picks:** `get_screenshot` each ambiguous slide's column (or the grid in chunks) and show the curator. Ask per ambiguous slide via AskUserQuestion ("Slide 4: A, B, or C?") or accept compact chat answers ("4→B, 9→C, rest A"). Unmentioned slides default to A.
4. **Assemble the final deck row:** move each chosen variant to y = 0 at its slide x; rename sequentially (`Slide 04 — <title>`); refresh page numbers via `applyDeckChrome` (total = final slide count); write the Step 5.6 records for the layout picks FIRST, then DELETE all losing variants.
5. **Log every decision** per Step 5.6 (written before the losing variants are deleted, per item 4) — including default-A confirms (chosen = A's template, rejected = B's and C's).

## Step 5: Generate in Figma

### 5a. Create the Output Page

Make a single `use_figma` call to create a new page:

```javascript
// Create output page
const pageName = "Generated - [SOURCE_NAME] - [DATE]";
const page = figma.createPage();
page.name = pageName;
return { pageId: page.id, pageName: page.name };
```

Always pass `skillNames: "figma-use"` when calling `use_figma`.

### 5b. Generate Each Slide

For each slide, make ONE `use_figma` call that:
1. Switches to the template page to access templates
2. Clones the template
3. Moves the clone to the output page
4. Sets all text content
5. Returns the created node IDs

Here is the pattern for a standard text-based template (e.g., bullets, title, info, quote, metrics, etc.):

```javascript
// --- Slide N: [TEMPLATE_NAME] ---
// Step 1: Get template from the templates page
const templatePage = figma.root.children.find(p => p.id === "TEMPLATE_PAGE_ID");
await figma.setCurrentPageAsync(templatePage);
const template = figma.getNodeById("TEMPLATE_NODE_ID");

// Step 2: Clone it
const clone = template.clone();

// Step 3: Move to output page
const outputPage = figma.root.children.find(p => p.id === "OUTPUT_PAGE_ID");
await figma.setCurrentPageAsync(outputPage);
outputPage.appendChild(clone);

// Step 4: Position — horizontal deck row (the project's canonical layout)
// In Curated mode, Step 4.5 dictates positions instead (variant A y=0, B y=1280, C y=2560).
clone.x = SLIDE_INDEX * 2120;
clone.y = 0;

// Step 5: Find and set text nodes
// IMPORTANT: skip text nodes whose name starts with '_legacy_' — those are quarantined
// stale slots from copy-paste history and are NOT part of the active vocabulary.
function findTextByName(node, name) {
  if (node.type === "TEXT" && node.name === name && !node.name.startsWith("_legacy_")) return node;
  if ("children" in node) {
    for (const child of node.children) {
      const found = findTextByName(child, name);
      if (found) return found;
    }
  }
  return null;
}

// For slots with duplicate names, find by original node ID within the clone
// When a node is cloned, child IDs change. We need to find the equivalent node
// by matching its position in the tree. The approach: find ALL text nodes with
// the given name and use the occurrence index.
function findTextByNameAtIndex(node, name, targetIndex) {
  const matches = [];
  function collect(n) {
    if (n.type === "TEXT" && n.name === name && !n.name.startsWith("_legacy_")) matches.push(n);
    if ("children" in n) {
      for (const child of n.children) collect(child);
    }
  }
  collect(node);
  return matches[targetIndex] || null;
}

async function loadFontAndSetText(textNode, value) {
  if (!textNode || !value) return;

  const origFont = textNode.fontName;
  if (origFont === figma.mixed) {
    const len = textNode.characters.length;
    const fontsToLoad = new Set();
    for (let i = 0; i < len; i++) {
      const f = textNode.getRangeFontName(i, i + 1);
      fontsToLoad.add(JSON.stringify(f));
    }
    for (const f of fontsToLoad) {
      await figma.loadFontAsync(JSON.parse(f));
    }
  } else {
    await figma.loadFontAsync(origFont);
  }

  textNode.characters = value;
}

async function setText(parent, slotName, value) {
  const textNode = findTextByName(parent, slotName);
  await loadFontAndSetText(textNode, value);
}

// For slots that need nodeId-based lookup (duplicate names in Figma):
// The registry specifies the ORIGINAL nodeId. After cloning, IDs change.
// Strategy: find all text nodes with the duplicate name and pick by index.
// The registry notes tell you which occurrence (e.g., 2nd "section-point-1").
// Use findTextByNameAtIndex(clone, "section-point-1", 1) for the second occurrence.
async function setTextByIndex(parent, name, index, value) {
  const textNode = findTextByNameAtIndex(parent, name, index);
  await loadFontAndSetText(textNode, value);
}

// IMPORTANT: All slot finders MUST skip text nodes whose name starts with '_legacy_'.
// These are quarantined stale nodes from copy-paste history (e.g., 'Beverage Description',
// 'Beverage title') that are NOT part of the active slot vocabulary. The Phase B harmonization
// renamed them with the '_legacy_' prefix instead of deleting (so they remain in Figma for
// reference). Any findByName / findByNameAtIndex implementation must filter them out:
//   if (n.name.startsWith('_legacy_')) return false;

// --- Trademark superscript node ---
// trademarks = contents of brand/trademarks.json (loaded in Step 1)

// Places a ™ or ® as a SEPARATE text node to the right of the slide's title node.
// Triggered when the title text contains a term from brand/trademarks.json.
// The mark is Suisse Int'l Regular at exactly half the title's font size.
// Top of the ™ node is top-aligned with the title bounding box (tm.y = titleBB.top).
// Named 'title-trademark' — idempotent (replaces any existing one).
// MUST be called AFTER setting the title text (title.width must reflect final characters).
async function placeTrademarkSuperscript(slide, titleNode, trademarks) {
  if (!titleNode || !trademarks) return null;
  const match = trademarks.terms.find(({ term }) => titleNode.characters.includes(term));
  if (!match) return null;

  // Remove any stale node (idempotent)
  const stale = slide.findOne(n => n.type === 'TEXT' && n.name === 'title-trademark');
  if (stale) stale.remove();

  const spec = trademarks.titleSuperscriptSpec;
  const tmFont = { family: spec.fontFamily, style: spec.fontStyle };
  await figma.loadFontAsync(tmFont);

  // Which line does the term appear on? (e.g. "Bluewater\nCafé Station 1" → line 1)
  const lines = titleNode.characters.split('\n');
  const termLine = Math.max(0, lines.findIndex(l => l.includes(match.term)));

  // Line height in px — used to offset tm.y to the correct line for multi-line titles
  const lh = titleNode.lineHeight;
  const lineHeightPx = lh.unit === 'PIXELS'  ? lh.value
                     : lh.unit === 'PERCENT' ? titleNode.fontSize * lh.value / 100
                     :                         titleNode.fontSize * 1.2;  // AUTO ≈ 120%

  // Measure the actual glyph width of the trademark line via a temp auto-sizing node.
  // Title containers are often fixed-width (full content area), so absoluteBoundingBox.width
  // ≠ actual text width — using it directly puts ™ in the far right margin.
  const titleFont = titleNode.fontName === figma.mixed
    ? titleNode.getRangeFontName(0, 1)
    : titleNode.fontName;
  await figma.loadFontAsync(titleFont);
  const measureNode = figma.createText();
  slide.appendChild(measureNode);
  measureNode.fontName = titleFont;
  measureNode.fontSize = titleNode.fontSize;
  measureNode.textAutoResize = 'WIDTH_AND_HEIGHT';
  measureNode.characters = lines[termLine] || titleNode.characters;
  const glyphWidth = measureNode.width;
  measureNode.remove();

  const tm = figma.createText();
  slide.appendChild(tm);
  tm.name = 'title-trademark';
  tm.fontName = tmFont;
  tm.fontSize = Math.round(titleNode.fontSize * spec.sizeRatio);
  tm.lineHeight = { unit: 'PERCENT', value: 110 };
  tm.characters = match.symbol;

  // For gradient fills use the last stop (highest position) as a solid color —
  // the ™ sits at the end of the title text, which maps to the gradient's end color.
  // Applying a gradient directly to the ™'s tiny bounding box compresses it oddly.
  function solidFillsFromTitle(fills) {
    return fills.map(fill => {
      if (!fill.type.startsWith('GRADIENT')) return JSON.parse(JSON.stringify(fill));
      const endStop = [...fill.gradientStops].sort((a, b) => b.position - a.position)[0];
      return { type: 'SOLID',
               color: { r: endStop.color.r, g: endStop.color.g, b: endStop.color.b },
               opacity: endStop.color.a ?? 1 };
    });
  }
  tm.fills = solidFillsFromTitle(titleNode.fills);
  tm.textAutoResize = 'WIDTH_AND_HEIGHT';

  // Position using absolute bounding boxes so nesting depth doesn't matter.
  // x: after the GLYPH right edge (not container right edge — containers are often full-width).
  // y: offset by line index so ™ top-aligns with the line carrying the trademark term.
  const slideBB = slide.absoluteBoundingBox;
  const titleBB  = titleNode.absoluteBoundingBox;
  const containerX = titleBB.x - slideBB.x;
  const align = titleNode.textAlignHorizontal;  // 'LEFT', 'CENTER', 'RIGHT'
  const glyphLeft = align === 'CENTER' ? containerX + (titleBB.width - glyphWidth) / 2
                  : align === 'RIGHT'  ? containerX + (titleBB.width - glyphWidth)
                  :                      containerX;  // LEFT or MIXED
  tm.x = glyphLeft + glyphWidth + (spec.gapPx ?? 0);
  tm.y = (titleBB.y - slideBB.y) + termLine * lineHeightPx;

  return { nodeId: tm.id, symbol: match.symbol, size: tm.fontSize,
           x: Math.round(tm.x), y: Math.round(tm.y) };
}

// Set all slot values for this template using plain setText() for all slots.
// After setting the title, call placeTrademarkSuperscript for any slide whose title
// contains a product or technology name (see brand/trademarks.json terms).
await setText(clone, "title", "ACTUAL TITLE TEXT");
const titleNode = findTextByName(clone, "title");
await placeTrademarkSuperscript(clone, titleNode, trademarks);  // no-op if no term matches

await setText(clone, "bullet-heading-1", "ACTUAL HEADING 1");
await setText(clone, "bullet-body-1", "ACTUAL BODY 1");
// ... continue for all slots defined in the registry for this template

// For duplicate-name slots (findBy: "nodeId"):
// Check the registry entry's "note" field for which occurrence to target
// Example: await setTextByIndex(clone, "section-point-1", 1, "Second section's first point");

return { slideIndex: SLIDE_INDEX, nodeId: clone.id, template: "TEMPLATE_NAME" };
```

### 5b-colors. Color swatch rows (additive, post-fill)

After filling all text slots on a card, check the card's body copy for color mentions:

- **Trigger phrases:** "comes in N colors", "available in", "colorways", or an explicit color list in the body text.
- **Action:** read `design-system.md → "Color Swatch Row Pattern"` and add a `color-swatches` row to that card following the spec exactly (24 px dots, 10 px gap, x=48 set AFTER appendChild, y = text section bottom + 16 px).
- **Color list:** use the color names mentioned in the PDF / product content. Apply the White/Clear stroke rules from the design system; map all other names to their product hex values (see the spec table for Bluewater standard colors).
- **Idempotent:** hide any existing `color-swatches` child on the card before appending the new row.
- This is additive — it does not change the slide template, text slots, or audit outcome.

### 5b-product. Cloning a product slide (product-first path)

When Step 4 chose a **product slide** instead of a generic template, the build is the same
clone-move-fill pattern as 5b, with these differences:
1. The source page is the product's `pageId` (from `products/registry.json`), not the template page.
2. The slide is a **finished, on-brand shell** — only rewrite text slots. Do not restructure it.
3. Fill slots by their **semantic name** (the `slots` keys in the registry: `title`, `body`,
   `cell-heading-N`, `product-name`, `stat-value-1`, `col-heading-N`, `row-label-N`, `cell-<r>-<c>`,
   etc.). Leave any slot you have no content for at its current (verified) text — these are real
   product facts, not placeholders. **Never rewrite** `wordmark*` or `*-trademark` nodes — those are
   fixed brand marks (the ™/® and decorative SuperiorOsmosis wordmarks), NOT content.
4. **Re-chrome every cloned slide (REQUIRED).** A product source slide carries *its own* deck's
   chrome — a stale page number (e.g. `meta-right` "3/14" from the original 14-slide deck), a
   cover-specific `meta-top-right`, or **no meta at all** (the Kitchen Station slides were built
   without it). `meta-*` is per-deck chrome, not brand content — so call `applyDeckChrome(clone, …)`
   on every clone to set a consistent `meta-left` (deck label) + `meta-right` ("N/total" for THIS
   deck), re-pin `meta-right` to the right edge, and create the nodes when the source lacked them.
5. **Fit copy to the shell — never overflow (REQUIRED).** Each shell text box is sized for its
   *original* copy length (most are `textAutoResize:"HEIGHT"`: fixed width, auto-growing height, so
   longer copy silently grows DOWN into the elements below — no error). So **rewrite each slot to
   roughly the original slot's length** (the original text is in the registry `slots`); if your copy
   is materially longer, condense it (apply the Step 3 "Condense" treatment to that slot regardless
   of the deck-wide choice). Fill via `fitShellText`, which condenses-then-shrinks-then-flags as a
   safety net. Anything it flags as `overflow:true` goes in the Step 6 summary for a human glance.

```javascript
// --- Slide N: PRODUCT clone (e.g. purifiers / purifier-comparison-table) ---
const productPage = figma.root.children.find(p => p.id === "PRODUCT_PAGE_ID"); // products.<slug>.pageId
await figma.setCurrentPageAsync(productPage);
const source = await figma.getNodeByIdAsync("PRODUCT_SLIDE_NODE_ID");          // slide.nodeId
const clone = source.clone();

const outputPage = figma.root.children.find(p => p.id === "OUTPUT_PAGE_ID");
await figma.setCurrentPageAsync(outputPage);
outputPage.appendChild(clone);
clone.x = SLIDE_INDEX * 2120;
clone.y = 0;

// Fill slots with overflow protection (reuse setText from 5b inside fitShellText):
const flags = [];
flags.push(await fitShellText(clone, "title", "REWRITTEN TITLE"));   // condense to ~original length
flags.push(await fitShellText(clone, "body",  "REWRITTEN BODY"));
// duplicate-named cells: fitShellText resolves by name; for the Nth duplicate use the index variant.

// Append ™/® superscript node after the title is final (title.width must be settled first)
const cloneTitleNode = clone.findOne(n => n.type === 'TEXT' && n.name === 'title');
await placeTrademarkSuperscript(clone, cloneTitleNode, trademarks);

// Re-chrome with THIS deck's labels + page number (update-or-create; covers keep their top label).
await applyDeckChrome(clone, { metaLeftText: DECK_LABEL, slideNumber: SLIDE_INDEX + 1, totalSlides: DECK_TOTAL, isDark: SLIDE_IS_DARK });

return { slideIndex: SLIDE_INDEX, nodeId: clone.id, product: "PRODUCT_SLUG", frame: "FRAME_NAME",
         overflow: flags.filter(f => f && f.overflow).map(f => f.slot) };
```

```javascript
// Update-or-create per-deck chrome on a cloned slide. (mkText: see design-system.md applyChrome.)
async function applyDeckChrome(slide, { metaLeftText, slideNumber, totalSlides, isDark = false }) {
  const gray = isDark ? {r:0xA1/255,g:0xA1/255,b:0xAA/255} : {r:0x71/255,g:0x71/255,b:0x7A/255};
  const find = (name) => slide.findOne(n => n.type === "TEXT" && n.name === name);
  // Cover convention: a single meta-top-right label, no page number — just refresh its text.
  const coverMeta = find("meta-top-right") || find("meta-top-left");
  if (coverMeta && !find("meta-left")) { await setText(coverMeta, coverMeta.name, metaLeftText); return { cover: coverMeta.id }; }
  // Content slide: deck label (left) + page number (right), created if the source had none.
  let ml = find("meta-left");
  if (ml) await setText(ml, "meta-left", metaLeftText);
  else ml = mkText(slide, metaLeftText, { size:14, style:"Regular", color:gray, x:48, y:48, name:"meta-left" });
  let mr = find("meta-right");
  const page = `${slideNumber}/${totalSlides}`;
  if (mr) await setText(mr, "meta-right", page);
  else { mr = mkText(slide, page, { size:14, style:"Regular", color:gray, name:"meta-right" }); mr.y = 48; }
  mr.textAlignHorizontal = "RIGHT"; mr.x = 1872 - mr.width;   // always re-pin right edge to x=1872
  return { metaLeft: ml.id, metaRight: mr.id };
}

// Fill a shell slot without overflowing it: condense (your job, in the value) → shrink → flag.
async function fitShellText(slide, slotName, value, { maxGrowth = 1.15 } = {}) {
  const t = slide.findOne(n => n.type === "TEXT" && n.name === slotName);
  if (!t) return { slot: slotName, set: false };
  const origH = t.height;                                 // height the shell was designed for
  await setText(t, slotName, value);                      // HEIGHT auto-resizes on new characters
  let shrunk = 0;
  while (t.height > origH * maxGrowth && t.fontSize > 14 && shrunk < 6) { t.fontSize = t.fontSize - 2; shrunk++; }
  return { slot: slotName, set: true, origH: Math.round(origH), grewTo: Math.round(t.height),
           shrunkBy: shrunk * 2, overflow: t.height > origH * maxGrowth };
}
```

**Audit:** product slides are finished/custom layouts — audit them with `kind: "skip"` (covers
"clones of finished slides"), so the slideContract content-grid checks don't fight their bespoke
geometry. `applyDeckChrome` already re-pins `meta-right`; re-anchor bottom content only if you hid a
slot (you usually won't). Report any `fitShellText` `overflow:true` slots in the Step 6 summary.

### 5c. Table Template Special Handling

Table templates use component instances for cells. The text is inside instance children. Use this pattern:

```javascript
// For table templates, find text inside instances by traversing all children
function findAllText(node, results = []) {
  if (node.type === "TEXT") {
    results.push(node);
  }
  if ("children" in node) {
    for (const child of node.children) {
      findAllText(child, results);
    }
  }
  return results;
}

// After cloning, find the table container (named "Table-4-columns" or similar)
function findFrameByName(node, name) {
  if (node.name === name && node.type === "FRAME") return node;
  if ("children" in node) {
    for (const child of node.children) {
      const found = findFrameByName(child, name);
      if (found) return found;
    }
  }
  return null;
}

// The table structure is: rows (frames) containing instances (Column-title, Row-title, Table-data)
// Each instance has one text child
// Process row by row, cell by cell
const tableFrame = findFrameByName(clone, "Table-4-columns");
const rows = tableFrame.children.filter(c => c.type === "FRAME" || c.type === "INSTANCE");

for (let rowIdx = 0; rowIdx < rows.length; rowIdx++) {
  const row = rows[rowIdx];
  if (row.type !== "FRAME") continue; // Skip vector separators

  const cells = row.children.filter(c => c.type === "INSTANCE");
  for (let colIdx = 0; colIdx < cells.length; colIdx++) {
    const cell = cells[colIdx];
    const textNodes = findAllText(cell);
    if (textNodes.length > 0) {
      const textNode = textNodes[0];
      await figma.loadFontAsync(textNode.fontName);
      textNode.characters = TABLE_DATA[rowIdx][colIdx]; // Your data array
    }
  }
}
```

### 5d. Image Placement (vision-indexed)

Image choice is a two-stage match against `assets/library.json` (v2: every asset carries a `visual` block), with preference boosts from `assets/preferences.json`. If the library is empty, skip image placement and note that `/import-assets` or `/sync-assets` should be run first.

#### 5d.1 Rank candidates per image slot

For each entry in the template's `imageSlots`:

1. **Semantic score (0–3):** compare the slide's title/topic/keywords against each asset's `tags` + `description`. 3 = direct subject match (slide about Spirit → asset tagged `spirit`); 2 = same family (any purifier asset for a purifier-range slide); 1 = generic brand-fit only (lifestyle/texture); 0 = unrelated. Discard 0s.
2. **Geometric filter (hard pass/fail):**
   - Slot aspect: from the registry entry's `w`/`h` when present (e.g. split-portrait 900×1023 → 0.88); otherwise by `size` tier using a single representative aspect: `small` = 1.3, `medium` = 1.6, `large` = 1.9; `background-image` roles = 1.78 (full slide). A slot with neither `w`/`h` nor `size` skips the aspect check (semantic + suitability filters still apply). Required slots = the registry's `imageSlots` entries only — a template may have more visual cards than image slots (see `imageSlotsNote`).
   - PASS when the asset's `visual.aspect` is within ±25% of the slot aspect, OR `visual.subject` is `center` (center-subject images crop safely under FILL).
   - `background-image` / hero roles additionally require `full-bleed` or `hero` in `visual.suitability` AND `visual.quality == "high"`.
   - Card/cell slots require at least one of `card`/`detail`/`hero` in `suitability`.
3. **Preference boost (tie-breaker):** read `assets/preferences.json → imagePicks`. +1 to an asset `chosen` for a similar context (same role or topic family); −1 when `rejected` in ≥2 similar contexts. Boosts never rescue a geometric FAIL.
4. **Rank** passing candidates by semantic score + boost. Top pick is applied now; the next 2–3 become the alternates strip in Curated mode (Step 5.5).

#### 5d.2 Apply with tone/subject rules

Copy the fill from the asset node to the slot (same page-switch pattern as before), forcing FILL:

```javascript
const assetPage = figma.root.children.find(p => p.id === "ASSET_PAGE_ID");
await figma.setCurrentPageAsync(assetPage);
const assetNode = await figma.getNodeByIdAsync("ASSET_NODE_ID");
const fills = JSON.parse(JSON.stringify(assetNode.fills));
for (const f of fills) if (f.type === "IMAGE") f.scaleMode = "FILL";

const outputPage = figma.root.children.find(p => p.id === "OUTPUT_PAGE_ID");
await figma.setCurrentPageAsync(outputPage);
const target = clone.findOne(n => n.name === "SLOT_NAME");  // or by role/position per registry note
target.fills = fills;
```

Note: asset nodeIds are global — the asset node may live on any page (see `assets/library.json` note); switch to the page that holds it, or rely on `getNodeByIdAsync` which loads it regardless.

On image-overlay templates (`full-bleed-hero`, `full-bleed-tech-hero`, `cover-with-product`):
- Text variant follows the asset's `visual.tone`: `light` image → dark text (`isDark: false` chrome), `dark`/`mixed` → light text (`isDark: true`).
- Prefer candidates whose `visual.subject` keeps the bottom-left title zone clear (`right`/`top` best; `bottom`/`left` allowed only if nothing better passes — flag for Step 6 QA legibility check).

#### 5d.3 No-placeholder gate (REQUIRED)

A FIG placeholder must NEVER survive into the final deck. If ranking leaves any required image slot without a passing candidate, do not build the image template — **re-route the slide to its text-first equivalent** and record the re-route for the Step 6 summary:

| Image template | Text-first re-route |
|---|---|
| `pillar-grid-4up-image` | `template-bento4` |
| `pillar-grid-3up-*` | `template-bento3` |
| `pillar-grid-large-image` | nearest no-`imageSlots` template matching the item count; if >6 items, condense to the 6 strongest and list the dropped items in the Step 6 summary |
| `bento-mix-center-hero` | `template-bento5` |
| `full-bleed-hero` / `full-bleed-tech-hero` | `template-chapter-left` (title only — body is dropped; if the body copy is substantive, use `template-info-left-middle` instead) |
| `cover-with-product` | `template-title-subtitle-left` |
| `split-portrait` | `template-info-left-middle` |
| `template-product-2` / `-3` | `template-bento2` / `-bento3` |
| `bento-3up-delivery` | `template-bento3` |
| `template-info-Nbullets` | same template — find each `Bullet-image-N` frame on the clone, set `visible = false`, then re-anchor per 5e (these frames are NOT in `optionalSlots`; hide them directly) |
| anything else | nearest no-`imageSlots` template with the same item count |

**All-or-nothing per slide:** if a multi-slot template (e.g. 3 pillars) has passing candidates for only SOME slots, re-route anyway — a mix of real images and placeholders is worse than a clean text slide. Exception: slots listed in the template's `optionalSlots` may be hidden instead (then re-anchor per 5e).

### 5e. Re-anchor bottom-justified content (REQUIRED)

Template containers are auto-layout frames that **hug** their content. When you hide an optional slot, the frame shrinks but stays pinned at its original top `y`, so the remaining content floats mid-slide instead of bottom-anchoring. You will not get an error — the slide is just silently wrong (this bit slides 8/12/15/18/26 in the first Beam build).

**The system:** the registry tags the affected containers per template under a `bottomAnchored` array, e.g. `"bottomAnchored": [{ "frame": "Frame 2956", "region": "slide" }]`. `region: "slide"` means the frame's bottom edge belongs at **y=1032** (48px from the slide bottom). `region: "card"` means its bottom belongs **48px above its parent card/column's bottom**. `"occurrence": "all"` re-anchors every frame of that name (e.g. comparison-3up has one per column).

**Run `anchorBottom(clone, template)` at the END of every slide build** — after all text is set and all slots hidden, so each frame reports its final shrunken height:

```js
// Re-anchor every bottomAnchored container declared for this template in registry.json.
// `anchors` = registry.templates[templateName].bottomAnchored  (pass [] if absent)
function anchorBottom(clone, anchors) {
  const moved = [];
  for (const a of (anchors || [])) {
    const frames = (a.occurrence === "all")
      ? clone.findAll(n => n.name === a.frame && n.type === "FRAME")
      : [clone.findOne(n => n.name === a.frame && n.type === "FRAME")].filter(Boolean);
    for (const f of frames) {
      // height is correct only AFTER hidden children shrank the hugging frame
      if (a.region === "slide") {
        f.y = 1032 - f.height;                       // bottom edge → y=1032
      } else if (a.region === "card") {
        const parentH = f.parent.height;             // card/column height (e.g. 745)
        f.y = (parentH - 48) - f.height;             // 48px above the card bottom
      }
      moved.push({ frame: f.name, y: Math.round(f.y) });
    }
  }
  return moved;
}
```

This is the executable counterpart to the design-system "Bottom-anchor rule". When you use a template that floats content on slot-hide and it is **not** yet tagged, add a `bottomAnchored` entry to that template in `registry.json` (verify the container frame name first) — that's how coverage grows. Untagged templates are not auto-corrected.

**Re-pin `meta-right` after editing its text (REQUIRED).** `meta-right`'s right edge belongs at x=1872 (48px from the slide edge). Several templates (tables, comparison, timeline) ship it LEFT-aligned at a fixed x to match a placeholder width — so when you replace the text on the clone, the right edge drifts (a shorter string lands ~105px from the edge). After setting `meta-right` on any cloned slide, re-pin it:

```js
async function repinMetaRight(clone) {
  const m = clone.findOne(n => n.type === "TEXT" && n.name === "meta-right");
  if (!m) return null;
  const f = m.fontName;                       // load font first — alignment is a font-dependent mutation
  if (f === figma.mixed) { for (let i=0;i<m.characters.length;i++) await figma.loadFontAsync(m.getRangeFontName(i,i+1)); }
  else { await figma.loadFontAsync(f); }
  m.textAlignHorizontal = "RIGHT";
  m.x = 1872 - m.width;                        // right edge → 1872
  return m.id;
}
```

`meta-left` is LEFT-anchored at x=48 and grows rightward, so it never drifts. See design-system.md → applyChrome note.

**Titles & display copy:** never leave a single-word widow on a wrapped title — bind the final 2–3 words with non-breaking spaces (` `) so the last line carries ≥2 words; do not hard-break with `\n`. Header paragraphs beside the title use the 587px prose column (x=1285, right edge 1872), not an arbitrary narrow width. See design-system.md → "No widows" and "Prose max-width".

### 5f. Batch Size

- Process slides one at a time (one `use_figma` call per slide)
- For presentations with 15+ slides, inform the user about progress every 5 slides
- If a slide fails, log the error and continue with the next slide

### 5g. Audit slide geometry (regression gate)

All registry templates now conform to `slideContract` at the source (every frame passes the `auditFrame` template-contract test — see `design-system.md`). So a clone is on-spec by construction. `auditSlide` is the **regression gate** that proves it — not a crutch you lean on to repair broken frames.

**After building each slide, run `auditSlide(slide, kind)`** (defined in `design-system.md`). It checks the slide against `registry.json → slideContract` (margins 48, title 64@y115 / intro 96, slide body 28 / intro 40, content top y287, last element bottom y1032). `kind` is `"content"`, `"intro"`, or `"skip"` (covers/heroes/full-bleed/closing/clones of finished slides/custom one-offs).

- If `auditSlide` returns issues, that means a **template frame has drifted** — STOP and fix the frame at the source (and run the `auditFrame` template-contract test to find any others), don't paper over it per-slide.
- This is the executable counterpart to `auditChrome` but covers **margins, title size, card-body size, and card-bottom anchoring**, not just chrome position.
- At the end of the build, re-run `auditSlide` across every generated slide as a final gate and report any remaining deviations in the summary.

## Step 5.5: Image pass (Curated mode only)

After assembly, for every slide with `imageSlots` where §5d.1 ranked ≥2 passing candidates:

1. **Build the alternates strip** below the slide (y = slide.y + 1180): for each runner-up (max 3), a rectangle 300px wide (height per the candidate's aspect) filled with the candidate image (FILL), laid out left-to-right with 32px gaps from the slide's x. Label each with a 24px text node: `S04-B`, `S04-C`, `S04-D`. Group strip + labels in a frame named `S04-alternates`. Slides whose slot had only one passing candidate get no strip.
2. **Collect swaps:** `get_screenshot` each slide column including its strip — capture from y = 0 down to the strip bottom (≈ y = 1700), not just the 1080px slide; show the curator; accept "4 → C"-style answers (AskUserQuestion or chat). Unmentioned slides keep their top pick.
3. **Apply swaps:** copy the chosen alternate's fill onto the slide's slot per §5d.2 — including the tone rule: if the new image's `visual.tone` differs, flip the text variant to match.
4. **On final confirm:** DELETE every `S*-alternates` frame; re-run `auditSlide` on swapped slides; proceed to Step 6 (the imagery QA gate covers the swapped images too).

## Step 5.6: Log preferences (Curated mode only)

Append one record per curation decision to `assets/preferences.json` (create as `{"imagePicks": [], "templatePicks": []}` if missing):

```jsonc
// layout pick (one per slide that had alternatives; confirming A counts)
{ "context": { "contentShape": "<e.g. '4 items, image-rich'>", "deck": "<deck label>" },
  "chosen": "<template name, 'custom', or 'product:<slug>/<role>'>",
  "rejected": ["<losing template names>"], "date": "<YYYY-MM-DD>" }

// image pick (one per slide that had a strip; keeping the top pick counts)
{ "context": { "role": "<slot role or template category>", "topic": "<slide topic>", "slot": "<imageSlot name/role>" },
  "chosen": "<winning assetKey>", "rejected": ["<losing assetKeys>"], "date": "<YYYY-MM-DD>" }
```

Records must be complete to be useful: populate every `context` sub-key (the §5d.1 boost and the Step 4 tie-breaker match on them — an empty context validates but never matches), and product picks must use the full `product:<slug>/<role>` form, never a bare `product:<slug>`.

Then run `python3 tools/validate_assets.py` — must end `OK`. These records feed the §5d.1 preference boost and the Step 4 template tie-breaker on every future run.

## Step 6: Verify and Report

After all slides are generated:

1. **Imagery QA gate (REQUIRED):** `get_screenshot` EVERY slide that carries an image (placed asset or overlay). Check each against:
   - Real image present — no FIG placeholder survived (if one did, the 5d.3 gate was skipped: re-route the slide now).
   - Text legible over the image (overlay templates): title/meta readable against the actual pixels behind them. If not, flip the text variant per `visual.tone`, or swap to the next-ranked candidate and re-check.
   - No awkward crop: the subject isn't cut off by FILL cropping. If it is, swap to the next-ranked candidate (prefer `subject: center`) and re-check.
   Fix what is fixable; anything still failing goes in the summary as "needs manual attention" with the reason.
2. `get_screenshot` a few text-only slides as a spot check.
3. Present a summary to the user:

```
Presentation generated successfully!

Page: "Generated - [name] - [date]"
Slides created: N/N

Slide summary:
1. ✓ [template-title-subtitle-center] "Company Overview"
2. ✓ [template-chapter-left] "Our Mission"
3. ✓ [template-bullets-4] "Key Products"
...

Any slides that need manual attention:
- Slide 7: Content was condensed from 5 to 4 bullets
- Slide 12: Logo garden template used — logos need to be added manually

Re-routed slides:
- Slide 9: pillar-grid-4up-image → template-bento4 (no passing image candidates)
```

4. Ask if they want to iterate on any specific slides

## Error Handling

- If `use_figma` fails for a slide, report the error and continue with remaining slides
- If the PDF cannot be read, ask the user to verify the file path
- If a template node cannot be found (ID changed), report which template failed and suggest the user check that the templates page still exists
- Never retry a failed `use_figma` call without first understanding and fixing the error

## Important Notes

- Templates use **Suisse Int'l** (Semi Bold, Medium, Regular) — the `loadFontAndSetText` function loads the original font and sets text
- Page context resets between `use_figma` calls — always switch to the correct page at the start of each call
- Use `await figma.setCurrentPageAsync(page)` — the sync setter (`figma.currentPage = page`) throws an error
- Do NOT use `figma.notify()` — it throws "not implemented"
- Do NOT use `console.log()` for output — use `return`
- Do NOT wrap code in an async IIFE — it's auto-wrapped
- Do NOT call `figma.closePlugin()`
