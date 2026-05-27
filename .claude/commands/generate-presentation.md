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
- `templatePageId`: The page containing all templates (`50285:14832`)
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

### Matching Priority

The registry has two `templatePages`: **"Template references"** (status `primary`, page id `56881:463`) and **"Templates 4"** (status `deprecated`, id `50285:14832`). Each template entry has a `page` field plus a `status` field (`KEEP` / `OVERLAP` / `DEPRECATE`). Walk the priority list below — references-page templates come first, deprecated ones last.

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
18. **Logos** → `template-logo-garden-3x3` (KEEP)
19. **Side-by-side comparison** → `template-comparison-50-50` (OVERLAP)
20. **Timeline / roadmap** → `template-timeline-bento`, `-timeline-cards`, or `-timeline-horizontal` (OVERLAP)
21. **Generic 2–6 bento (no clear hero, no imagery available)** → `template-bento2`/`-bento3`/`-bento4`/`-bento5`/`-bento6`, or asymmetric `template-bento-25-75` / `-33-66` / `-66-33` / `-75-25` (OVERLAP)
22. **Title + 2-4 supporting bullets** → `template-info-2bullets`, `-3bullets`, or `-4bullets` (OVERLAP)
23. **Title + paragraph + image** → `template-info-left-middle`, `-info-left-top`, `-info-left-bottom`, `-info-center-center`, `-info-split-top` (OVERLAP)
24. **Product showcase, 2–3 products without pricing** → `template-product-2` or `template-product-3` (OVERLAP)
25. **Checklist** → `template-checklist-bento` (OVERLAP)
26. **Anything that fits no template above** → **CREATIVE ESCAPE HATCH** (build from scratch — see Creative Decision Rules)

**DEPRECATE — do not use unless user explicitly opts in:** `template-bullets-4`, `-bullets-6`, `-bullets-8`, `template-technical-bullets`. The new pillar-grid / bento patterns above replace these for nearly every content shape that previously matched bullet templates.

### Creative Decision Rules

Before finalizing template selection, apply these judgment calls:

**Prefer Template references over Templates 4.** When two candidates match (e.g., a 4-item shape could fit `pillar-grid-4up-image` OR `template-bento4`), pick the references-page entry. The references are the canonical Bluewater style; Templates 4 entries are kept for fallback only.

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

// Step 4: Position (slide index * (1080 + 200) spacing)
clone.x = 0;
clone.y = SLIDE_INDEX * 1280;

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

// Set all slot values for this template
// For standard slots (findBy: "name"):
await setText(clone, "title", "ACTUAL TITLE TEXT");
await setText(clone, "bullet-heading-1", "ACTUAL HEADING 1");
await setText(clone, "bullet-body-1", "ACTUAL BODY 1");
// ... continue for all slots defined in the registry for this template

// For duplicate-name slots (findBy: "nodeId"):
// Check the registry entry's "note" field for which occurrence to target
// Example: await setTextByIndex(clone, "section-point-1", 1, "Second section's first point");

return { slideIndex: SLIDE_INDEX, nodeId: clone.id, template: "TEMPLATE_NAME" };
```

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

### 5d. Image Placement

After filling text on a slide, check if the template has `imageSlots` in the registry. If it does AND `assets/library.json` has assets:

1. Read the slide's content context (title, topic keywords)
2. Match assets from the library by comparing tags to the slide context
3. For each image slot, copy the image fill from the matched asset node

```javascript
// Image placement: copy fill from Brand Assets page node to slide placeholder
// Must switch to Brand Assets page to access the asset node, then back to output page

const assetPage = figma.root.children.find(p => p.id === "ASSET_PAGE_ID");
await figma.setCurrentPageAsync(assetPage);
const assetNode = figma.getNodeById("ASSET_NODE_ID");
const assetFills = JSON.parse(JSON.stringify(assetNode.fills));

const outputPage = figma.root.children.find(p => p.id === "OUTPUT_PAGE_ID");
await figma.setCurrentPageAsync(outputPage);

// Find the image slot in the cloned slide by name
function findFrameByName(node, name) {
  if (node.name === name) return node;
  if ("children" in node) {
    for (const c of node.children) {
      const f = findFrameByName(c, name);
      if (f) return f;
    }
  }
  return null;
}

const target = figma.getNodeById("CLONED_IMAGE_SLOT_NODE_ID");
// Or find by traversal if IDs changed after cloning:
// const target = findFrameByName(clone, "Bento-50");

target.fills = assetFills;
```

**Important notes:**
- Image slots are identified by their original `nodeId` in the registry. After cloning, you need to find the equivalent node in the clone by name or position.
- If no matching asset exists for a slot, leave it as-is (the template's default fill) and note it in the report.
- The user can override image choices: *"Use cafe-station-1-hero on slide 4"*
- If the asset library is empty, skip image placement entirely and note that `/sync-assets` should be run first.

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

### 5f. Batch Size

- Process slides one at a time (one `use_figma` call per slide)
- For presentations with 15+ slides, inform the user about progress every 5 slides
- If a slide fails, log the error and continue with the next slide

## Step 6: Verify and Report

After all slides are generated:

1. Use `get_screenshot` on a few slides from the output page to visually verify
2. Present a summary to the user:

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
```

3. Ask if they want to iterate on any specific slides

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
