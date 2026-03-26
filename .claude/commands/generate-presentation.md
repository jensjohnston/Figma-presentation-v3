# Generate Figma Presentation from PDF

Convert a PDF presentation into an on-brand Bluewater Figma deck using pre-made templates.

## Usage
```
/generate-presentation <path-to-pdf>
```

The user provides a path to a PDF file. You will read it, analyze each slide, match it to the best Bluewater template, and generate the full presentation in Figma.

## Important: Load the figma-use skill

Before calling any `use_figma` MCP tool, you MUST invoke the `figma:figma-use` skill. This is mandatory for every session.

## Step 1: Read the Template Registry

Read the file `templates/registry.json` from the project root. This contains:
- `fileKey`: The Figma file key (`hOEre1lPHVpPdv2U9u7RFa`)
- `templatePageId`: The page containing all templates (`50285:14832`)
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

## Step 3: Match Each Slide to a Template

For each extracted slide, select the best template from the registry using these rules (in priority order):

### Matching Priority
1. **First slide** → Use a title template (`template-title-subtitle-center` if it has a subtitle, `template-title-center` if title only)
2. **Slide with only a short heading (1-5 words), no body** → Chapter divider (`template-chapter-left` or `template-chapter-center`)
3. **Single large number/stat** → `template-huge-fact` (number only), `template-huge-fact-eyebrow` (number + label above), or `template-huge-fact-body` (number + explanation below)
4. **Multiple metrics (3-4 numbers)** → `template-metrics-4`
5. **Quote with attribution** → `template-quote1-middle` (1 quote) or `template-quote2-middle` (2 quotes)
6. **Side-by-side comparison** → `template-comparison-50-50`
7. **Bullet points with headings** → Count bullets, round UP:
   - 1-4 bullets → `template-bullets-4`
   - 5-6 bullets → `template-bullets-6`
   - 7-8 bullets → `template-bullets-8`
   - 9+ bullets → `template-technical-bullets`
8. **Table/structured data** → Count columns:
   - 2 columns → `template-table-2columns`
   - 3 columns → `template-table-3columns`
   - 4+ columns → `template-table-4columns`
9. **Product showcase** → `template-product-2` (2 products) or `template-product-3` (3 products)
10. **Info with supporting bullets** → `template-info-2bullets`, `template-info-3bullets`, or `template-info-4bullets`
11. **Title + body paragraph** → `template-info-left-middle` (this is the fallback for anything that doesn't match above)

### Content Adaptation Rules
- If text is too long for a slot, rewrite it more concisely while preserving meaning
- If a slide has 5 bullets but no template supports exactly 5, use `template-bullets-6` and leave one slot with a space character (" ")
- For table templates, if the source has more rows than the template supports (6 rows), summarize or truncate to fit
- Keep the original language and tone — do not add marketing speak that wasn't in the source

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

## Step 4: Generate in Figma

### 4a. Create the Output Page

Make a single `use_figma` call to create a new page:

```javascript
// Create output page
const pageName = "Generated - [SOURCE_NAME] - [DATE]";
const page = figma.createPage();
page.name = pageName;
return { pageId: page.id, pageName: page.name };
```

Always pass `skillNames: "figma-use"` when calling `use_figma`.

### 4b. Generate Each Slide

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

// Font override: Using Inter as temporary substitute for Suisse Int'l
// Maps the original font styles to Inter equivalents
const FONT_MAP = {
  "Semi Bold": { family: "Inter", style: "Semi Bold" },
  "Medium": { family: "Inter", style: "Medium" },
  "Regular": { family: "Inter", style: "Regular" },
};

async function loadFontAndSetText(textNode, value) {
  if (!textNode || !value) return;

  // Load the ORIGINAL font first (needed to read/modify the node)
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
    // Load Inter equivalents and swap
    for (let i = 0; i < len; i++) {
      const f = textNode.getRangeFontName(i, i + 1);
      const interFont = FONT_MAP[f.style] || FONT_MAP["Regular"];
      await figma.loadFontAsync(interFont);
    }
  } else {
    await figma.loadFontAsync(origFont);
    const interFont = FONT_MAP[origFont.style] || FONT_MAP["Regular"];
    await figma.loadFontAsync(interFont);
  }

  // Set the text content
  textNode.characters = value;

  // Now swap the font to Inter
  if (origFont !== figma.mixed) {
    const interFont = FONT_MAP[origFont.style] || FONT_MAP["Regular"];
    textNode.fontName = interFont;
  } else {
    // For mixed fonts, swap each range
    const len = textNode.characters.length;
    for (let i = 0; i < len; i++) {
      const f = textNode.getRangeFontName(i, i + 1);
      const interFont = FONT_MAP[f.style] || FONT_MAP["Regular"];
      textNode.setRangeFontName(i, i + 1, interFont);
    }
  }
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

### 4c. Table Template Special Handling

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

### 4d. Batch Size

- Process slides one at a time (one `use_figma` call per slide)
- For presentations with 15+ slides, inform the user about progress every 5 slides
- If a slide fails, log the error and continue with the next slide

## Step 5: Verify and Report

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

- Templates originally use "Suisse Int'l" but we override to **Inter** (Semi Bold, Medium, Regular) since custom fonts require Figma Organization plan
- The `loadFontAndSetText` function handles the font swap automatically: loads the original font, sets text, then swaps to Inter
- When Suisse Int'l becomes available, update the `FONT_MAP` in the code pattern to use `"Suisse Int'l"` instead of `"Inter"`
- Page context resets between `use_figma` calls — always switch to the correct page at the start of each call
- Use `await figma.setCurrentPageAsync(page)` — the sync setter (`figma.currentPage = page`) throws an error
- Do NOT use `figma.notify()` — it throws "not implemented"
- Do NOT use `console.log()` for output — use `return`
- Do NOT wrap code in an async IIFE — it's auto-wrapped
- Do NOT call `figma.closePlugin()`
