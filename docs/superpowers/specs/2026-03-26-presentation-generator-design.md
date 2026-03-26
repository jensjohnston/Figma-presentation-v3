# Presentation Generator Design Spec

**Date**: 2026-03-26
**Status**: Approved

## Problem

Bluewater's marketing team needs to quickly convert existing presentations (PDF) into on-brand Figma decks. Currently this is manual work — designers recreate slides by hand using brand templates.

## Solution

A Claude Code slash command (`/generate-presentation`) that:
1. Reads a PDF presentation
2. Analyzes each slide's content and structure
3. Auto-matches to the best Bluewater template from a registry of 41 templates
4. Generates the full deck in Figma via `use_figma` MCP tool

## Key Design Decisions

- **MCP-first**: No frontend, no build step, no runtime dependencies. Claude orchestrates everything.
- **Template registry**: Single JSON file (`templates/registry.json`) is the source of truth. Adding templates = adding JSON entries.
- **AI auto-matching**: Claude picks the best template per slide based on content analysis. No manual mapping needed.
- **One call per slide**: Each slide is generated in a single `use_figma` call (clone template → fill text). Independent, recoverable.
- **Output location**: New page in the existing Bluewater Figma file.

## Template Categories (41 total)

| Category | Count | Templates |
|----------|-------|-----------|
| Title | 4 | center, left, subtitle-center, subtitle-left |
| Bullets | 4 | 4, 6, 8, technical |
| Chapter | 3 | left, center, right |
| Comparison/Split | 5 | 50-50, 75-25, 25-75, 66-33, 33-66 |
| Bento Grid | 5 | 2, 3, 4, 5, 6 cells |
| Table | 3 | 2, 3, 4 columns |
| Quote | 2 | single, double |
| Metrics | 1 | 4 metrics |
| Huge Fact | 3 | plain, eyebrow, body |
| Info | 8 | left-top/mid/bottom, center, 2/3/4 bullets, split-top |
| Product | 2 | 2, 3 products |
| Logo Garden | 1 | 3x3 grid |

## Figma Generation Flow

```
use_figma: Create output page → return pageId
    ↓
For each slide:
  use_figma: Switch to template page → clone template → move to output page → fill text → return nodeId
    ↓
get_screenshot: Verify output visually
```

## Future Phases

- **Phase 2**: Image support (fill image slots in templates), PPTX input support
- **Phase 3**: Create presentations from scratch (topic brief → AI-generated content)
- **Phase 4**: PowerPoint export
