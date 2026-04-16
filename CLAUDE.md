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
3. Claude reads `templates/registry.json` (templates + typography system) and `templates/design-system.md` (grid rules, creative decisions)
4. Claude matches each slide to the best template — or builds from scratch using design system rules when content needs a custom layout
5. Claude generates slides in Figma via `use_figma` MCP tool (clone template → fill text, or build custom bento grids)
6. Output: new page in the Bluewater Figma file

## Design System

- `templates/design-system.md` — Grid construction, typography (including impact rules), bento card rules, color system, creative decision guide
- `templates/registry.json` — Template registry with `typography` spec and `flexible` metadata per template
- Templates with `flexible.buildFromScratch: true` can be rebuilt with different item counts using the grid system
- Templates with `flexible.optionalSlots` allow hiding unused text elements
- Templates with `flexible.impactSlots` allow scaling up dramatic numbers/phrases

## Template Font

Templates use **Suisse Int'l** (Semi Bold, Medium, Regular). Custom fonts are uploaded to the Figma org under Admin → Resources → Fonts.

## Adding New Templates

1. Design the template in Figma on "Templates 4" page
2. Use semantic text layer names: `title`, `body`, `bullet-heading-N`, `bullet-body-N`, `cell-heading-N`, `cell-body-N`, etc.
3. Add entry to `templates/registry.json` with nodeId, slots, and matchHints
