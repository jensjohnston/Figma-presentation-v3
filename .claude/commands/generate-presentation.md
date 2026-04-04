# Generate Figma Presentation from PDF

Convert a PDF presentation into an on-brand Bluewater Figma deck using pre-made templates.

## Usage
```
/generate-presentation <path-to-pdf>
```

The user provides a path to a PDF file. You will read it, analyze each slide, match it to the best Bluewater template, and generate the full presentation in Figma.

## Important: Load the figma-use skill

Before calling any `use_figma` MCP tool, you MUST invoke the `figma:figma-use` skill. This is mandatory for every session.

## Step 1: Read the Template Registry and Design Playbook

Read these files from the project root:

1. **`templates/registry.json`** — Contains:
   - `fileKey`: The Figma file key (`GkUiwJTK5Xi65AKw4MOjTL`)
   - `templatePageId`: The page containing all templates (`50285:14832`)
   - `templates`: A map of all 47 templates with their `nodeId`, `category`, `description`, `slots`, and `matchHints`

2. **`brand/presentation-playbook.md`** — The design playbook learned from reference presentations. This is critical — it teaches you:
   - The "highlight card" pattern (last/best card gets branded gradient treatment)
   - When and where to use product photography on slides
   - How to structure ingredient/feature cards with image backgrounds
   - The pricing/economics card layout with product imagery
   - The narrative arc that presentations should follow
   - Color system, typography hierarchy, and visual patterns

**You must read and internalize the playbook before proceeding.** It captures design decisions that go beyond template matching — it tells you HOW to compose each slide to look premium and on-brand.

You will use the registry and playbook together throughout the process.

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

### Question 3: Product / Visual Theme (Scene Templates)

Check `templates/registry.json` for the `sceneTemplates` section. If scene templates exist, ask:

**"Which product or visual style should this deck use?"**

Options (built dynamically from unique `product` values in `sceneTemplates`):
- List each available product (e.g., "Flowater Pilates — pink gradient, studio partner style")
- **"Mix freely / best match"** — pick the best-looking scene for each slide regardless of source
- **"Generic templates only"** — skip scenes entirely, use only layout templates

This sets the `preferredProduct` for scene matching in Step 4.

## Step 4: Match Each Slide to a Template

For each extracted slide, first try scene templates, then fall back to generic templates.

### Scene Pre-Match (try first)

If the user selected a product/theme (not "Generic templates only"), check `sceneTemplates` for each slide:

1. **Filter** by `matchCategories` — the scene must cover the slide's detected content category
2. **Filter** by slot compatibility — the scene must have enough swappable slots for the content
3. **Score** remaining candidates:
   - Preferred product match → **+3 points**
   - Matching audience → **+2 points**
   - Compatible visual theme with other selected scenes → **+1 point**
   - Exact slot count match → **+1 point**
4. **Pick** the highest-scoring scene. If tied, pick any.
5. If a scene matches → use it. Mark as **★ Scene** in the slide plan.
6. If no scene matches → fall through to generic matching below.

**Important:** When a scene template has `frozenVisuals: true`, all images, gradients, and visual compositions are baked into the template. Only the text in `slots` will be swapped. Do NOT attempt to modify images or backgrounds on scene slides.

### Generic Matching (fallback)

If no scene template matched, select the best generic template using these rules (in priority order):

### Matching Priority
1. **First slide** → Use a title template (`template-title-subtitle-center` if it has a subtitle, `template-title-center` if title only)
2. **Last slide with CTA / contact info / "get in touch"** → `template-cta-center`
3. **Slide with only a short heading (1-5 words), no body** → Chapter divider (`template-chapter-left` or `template-chapter-center`)
4. **Single large number/stat** → `template-huge-fact` (number only), `template-huge-fact-eyebrow` (number + label above), or `template-huge-fact-body` (number + explanation below)
5. **Multiple metrics (3-4 numbers)** → `template-metrics-4`
6. **Pricing / economics / scenarios** (3-4 items each with a prominent price/number + label + sublabel) → `template-pricing-cards-3` (3 items) or `template-pricing-cards-4` (4 items)
7. **Sequential process / steps** (3 numbered actions/phases) → `template-process-steps-3`
8. **Feature/ingredient cards with metrics** (3-4 items each with name + metric/value + description) → `template-feature-cards-3` (3 items) or `template-feature-cards-4` (4 items)
9. **Quote with attribution** → `template-quote1-middle` (1 quote) or `template-quote2-middle` (2 quotes)
10. **Side-by-side comparison** → `template-comparison-50-50`
11. **Bullet points with headings** → Count bullets, round UP:
   - 1-4 bullets → `template-bullets-4`
   - 5-6 bullets → `template-bullets-6`
   - 7-8 bullets → `template-bullets-8`
   - 9+ bullets → `template-technical-bullets`
12. **Table/structured data** → Count columns:
   - 2 columns → `template-table-2columns`
   - 3 columns → `template-table-3columns`
   - 4+ columns → `template-table-4columns`
13. **Product showcase** → `template-product-2` (2 products) or `template-product-3` (3 products)
14. **Info with supporting bullets** → `template-info-2bullets`, `template-info-3bullets`, or `template-info-4bullets`
15. **Title + body paragraph** → `template-info-left-middle` (this is the fallback for anything that doesn't match above)

### Content Pattern Detection Heuristics

Use these signals to classify ambiguous slides before matching:

**Pricing/economics pattern** → rules 6. Match when:
- Slide contains 3-4 items where each has a dollar amount, percentage, or large number as the primary element
- Content discusses costs, pricing tiers, margins, revenue scenarios, or financial projections
- Structure is: [label] + [big number] + [context/sublabel] repeated 3-4 times
- Signals: "$", "per month", "per year", "margin", "revenue", "cost", tier names like "Basic/Pro/Enterprise" or "Conservative/Moderate/Strong"

**Process/steps pattern** → rule 7. Match when:
- Slide describes a sequence of 3 actions, phases, or stages
- Content uses ordinal language ("First… then… finally", "Step 1/2/3", numbered items)
- Items have a temporal or causal relationship (order matters)
- Signals: numbered prefixes, "then", "next", "finally", time durations ("in 30 minutes"), imperative verbs

**Feature cards pattern** → rule 8. Match when:
- Slide presents 3-4 items where each has a name AND a quantitative detail (dosage, measurement, multiplier) AND a description
- Differs from bullets (which lack the metric/highlight value per item)
- Differs from bento (which is more visual/image-oriented)
- Signals: measurement units (mg, mL, x, %), ingredient/feature names as headings

**CTA/closing pattern** → rule 2. Match when:
- Slide is the last or near-last slide
- Contains contact information, a URL, email, or explicit call to action
- Uses language like "get in touch", "let's talk", "contact us", "get started", "next steps"

### Content Adaptation Rules
Apply the user's choices from Step 3 when filling content:
- **Content length**: If "Keep original", use verbatim text. If "Condense", rewrite shorter. If "Expand", add detail.
- **Voice**: If "Keep original", preserve the source tone. If "Bluewater brand voice", rewrite in brand voice (or use `brand/voice-guide.md` if available).
- If text is too long for a slot regardless of length choice, rewrite it more concisely while preserving meaning
- If a slide has 5 bullets but no template supports exactly 5, use `template-bullets-6` and leave one slot with a space character (" ")
- For table templates, if the source has more rows than the template supports (6 rows), summarize or truncate to fit

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
1. Switches to the **source page** (template page for generic templates, or the scene's `sourcePageId` for scene templates)
2. Clones the template/scene
3. Moves the clone to the output page
4. Sets all text content in the defined slots
5. **If `frozenVisuals: true`** (scene templates): skip ALL image placement — visuals are baked in
6. Returns the created node IDs

**Choosing the source page:** Check whether the matched template is from `sceneTemplates` or `templates`:
- **Scene template** → use `sourcePageId` from the scene entry (e.g., the finished deck page)
- **Generic template** → use `templatePageId` ("Templates 4") as before

**Finding text nodes in scene templates:** Scene templates often have non-standard text layer names (content used as name, like `"$3.50"` or `"Electrolytes"`). For these slots, the registry uses `"findBy": "nodeId"` with the original node ID. After cloning, child IDs change, so you CANNOT use `figma.getNodeById`. Instead, build a mapping: before cloning, traverse the source template to find the text node by its original ID and record its **path** (parent indices). After cloning, follow the same path in the clone to find the equivalent node.

Here is the helper function for nodeId-based slot lookup in cloned scenes:

```javascript
// Find a text node in a cloned tree by matching the structure path from the original
function findTextByOriginalId(originalParent, clonedParent, originalNodeId) {
  // Build path to the original node
  function findPath(node, targetId, path = []) {
    if (node.id === targetId) return path;
    if ("children" in node) {
      for (let i = 0; i < node.children.length; i++) {
        const result = findPath(node.children[i], targetId, [...path, i]);
        if (result) return result;
      }
    }
    return null;
  }
  
  const path = findPath(originalParent, originalNodeId);
  if (!path) return null;
  
  // Follow the same path in the clone
  let current = clonedParent;
  for (const idx of path) {
    if (!("children" in current) || idx >= current.children.length) return null;
    current = current.children[idx];
  }
  return current.type === "TEXT" ? current : null;
}
```

Here is the pattern for a standard text-based template (e.g., bullets, title, info, quote, metrics, etc.):

```javascript
// --- Slide N: [TEMPLATE_NAME] ---
// Step 1: Get template from the appropriate source page
// For scene templates: use the scene's sourcePageId
// For generic templates: use TEMPLATE_PAGE_ID
const sourcePage = figma.root.children.find(p => p.id === "SOURCE_PAGE_ID");
await figma.setCurrentPageAsync(sourcePage);
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
function findTextByName(node, name) {
  if (node.type === "TEXT" && node.name === name) return node;
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
    if (n.type === "TEXT" && n.name === name) matches.push(n);
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

### 5e. Batch Size

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
