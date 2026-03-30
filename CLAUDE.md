# Bluewater Presentation Generator

MCP-first tool that converts PDF presentations into on-brand Figma decks using pre-made templates.

## Quick Start

```
/generate-presentation path/to/deck.pdf
```

## Architecture

- **No build step, no runtime, no dependencies.** Claude is the engine.
- `templates/registry.json` — Maps 41 Bluewater slide templates to Figma node IDs and content slots
- `.claude/commands/generate-presentation.md` — Slash command orchestrating the full pipeline
- Figma file: `GkUiwJTK5Xi65AKw4MOjTL` (Bluewater 2026)
- Template page: "Templates 4" (id: `50285:14832`)

## How It Works

1. User provides a PDF
2. Claude reads it, extracts content per slide
3. Claude matches each slide to the best template from the registry
4. Claude generates slides in Figma via `use_figma` MCP tool (clone template → fill text)
5. Output: new page in the Bluewater Figma file

## Template Font

Templates are designed with **Suisse Int'l** but we currently override to **Inter** (Semi Bold, Medium, Regular) since custom fonts require Figma Organization plan. When the org plan is active, update the `FONT_MAP` in the slash command and `fontFamily` in `registry.json` back to `Suisse Int'l`.

## Adding New Templates

1. Design the template in Figma on "Templates 4" page
2. Use semantic text layer names: `title`, `body`, `bullet-heading-N`, `bullet-body-N`, `cell-heading-N`, `cell-body-N`, etc.
3. Add entry to `templates/registry.json` with nodeId, slots, and matchHints
