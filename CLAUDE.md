# Bluewater Presentation Generator

MCP-first tool that converts PDF presentations into on-brand Figma decks using pre-made templates.

## Quick Start

```
/generate-presentation path/to/deck.pdf
```

## Architecture

- **No build step, no runtime, no dependencies.** Claude is the engine.
- `templates/registry.json` — Maps 47 Bluewater slide templates to Figma node IDs and content slots
- `.claude/commands/generate-presentation.md` — Slash command orchestrating the full pipeline
- Figma file: `GkUiwJTK5Xi65AKw4MOjTL` (Bluewater 2026)
- Template page: "Templates 4" (id: `50285:14832`)

## How It Works

1. User provides a PDF
2. Claude reads it, extracts content per slide
3. Claude matches each slide to the best **scene template** (pre-composed visual scene from a finished deck) or falls back to a generic layout template
4. Claude generates slides in Figma via `use_figma` MCP tool (clone template → fill text)
5. For scene templates: visuals are frozen (product photos, gradients baked in) — only text is swapped
6. Output: new page in the Bluewater Figma file

## Scene Templates

Scene templates are extracted from finished, hand-crafted decks using `/extract-scenes`. They produce near-pixel-perfect output because the visual composition is already done — the generator only swaps text content.

- `sceneTemplates` in `registry.json` — maps scene templates with product/audience/theme tags
- `scenePages` in `registry.json` — lists source deck pages containing scenes
- `.claude/commands/extract-scenes.md` — command to extract new scenes from a finished deck
- `brand/presentation-playbook.md` — design patterns and scene selection guidance

## Template Font

Templates use **Suisse Int'l** (Semi Bold, Medium, Regular). Custom fonts are uploaded to the Figma org under Admin → Resources → Fonts.

## Adding New Templates

1. Design the template in Figma on "Templates 4" page
2. Use semantic text layer names: `title`, `body`, `bullet-heading-N`, `bullet-body-N`, `cell-heading-N`, `cell-body-N`, `card-label-N`, `card-value-N`, `card-heading-N`, `card-metric-N`, `step-heading-N`, `step-body-N`, `cta-label`, `cta-value`, `footer`, etc.
3. Add entry to `templates/registry.json` with nodeId, slots, and matchHints

## Template Categories

titles, chapters, bullets, bento grids, bento splits, tables, quotes, metrics, facts, info, products, logo gardens, **pricing cards**, **process steps**, **feature cards**, **CTA**
