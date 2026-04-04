# Extract Scenes from a Finished Presentation

Turn a hand-crafted Figma presentation into reusable scene templates for the presentation generator.

## Usage
```
/extract-scenes <figma-page-node-id> [deck-name]
```

The user provides the node ID of a finished presentation page in the Figma file. You will analyze each slide, identify swappable text slots, and register them as scene templates.

## Important: Load the figma-use skill

Before calling any `use_figma` MCP tool, you MUST invoke the `figma:figma-use` skill.

## Step 1: Read the Source Deck

Use `get_metadata` on the provided page node ID to enumerate all top-level frame children. Each frame is a slide.

Then use `get_screenshot` on the full page to see the visual overview.

## Step 2: Screenshot and Classify Each Slide

For each slide:
1. Use `get_screenshot` to see its visual composition
2. Classify it:
   - **category**: title, product, features, comparison, info, pricing, process, bullets, cta
   - **sceneType**: descriptive label (e.g., "pricing-3-highlight", "feature-cards-4-with-photos")
   - **visualTheme**: color/style family (e.g., "pink-gradient", "blue-dark", "neutral-light")

## Step 3: Audit Text Nodes

For each slide, use `use_figma` to traverse all visible TEXT nodes and record:
- Node name
- Node ID
- Current text content
- Font size

Classify each text node as:
- **Swappable slot**: Titles, body text, card labels, values, headings, descriptions — content that would change per presentation
- **Frozen decorative**: Logo text, brand marks (like "™"), watermarks — should NOT be changed

### Slot naming convention:
For swappable slots, determine the semantic slot name:
- Standard names (`title`, `body`, `eyebrow`, `footer`) → use `findBy: "name"`
- Non-standard names (content used as name, like `"$3.50"`) → use `findBy: "nodeId"` with the original node ID

## Step 4: Ask User for Product Metadata

Ask the user using AskUserQuestion:
1. **Product name** — e.g., "flowater-pilates", "opilatus"
2. **Target audience** — e.g., "studio-partners", "office", "home"
3. **Deck name** — for the `sourceDeck` field (use the argument if provided)

## Step 5: Register Scene Templates

Read `templates/registry.json` and add:

1. A new entry to `scenePages`:
```json
{
  "pageId": "<source page node ID>",
  "pageName": "<page name>",
  "sourceDeck": "<deck name>",
  "sourceNodeId": "<page node ID>"
}
```

2. For each slide, a new entry in `sceneTemplates`:
```json
"scene-<product>-<type>": {
  "nodeId": "<slide frame node ID>",
  "sourcePageId": "<page node ID>",
  "category": "<category>",
  "sceneType": "<scene type>",
  "frozenVisuals": true,
  "sourceDeck": "<deck name>",
  "product": "<product>",
  "audience": "<audience>",
  "visualTheme": "<theme>",
  "slots": [ ... ],
  "matchCategories": ["<category>"],
  "matchHints": "<description of when to use this scene>"
}
```

## Step 6: Present Summary

Show the user a table of all extracted scenes with:
- Scene name
- Category
- Number of swappable slots
- A one-line description

Ask for confirmation before writing to the registry.

## Notes

- Scene templates reference slides **in-place** on their original page. Do not clone or move slides.
- If the source deck is later edited, the scene templates will reflect those changes. This is intentional — it means improving a finished deck automatically improves the scene templates.
- The `frozenVisuals` flag tells the generator to skip all image/asset placement for scene slides.
- Each finished deck you extract adds to the scene library. Over time, the library covers more content patterns and more products.
