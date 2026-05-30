# Bluewater Presentation Generator

MCP-first tool that converts PDF presentations into on-brand Figma decks using pre-made templates.

## Quick Start

```
/generate-presentation path/to/deck.pdf
```

## Architecture

- **No build step, no runtime, no dependencies.** Claude is the engine.
- `templates/registry.json` — Maps the Bluewater slide templates to Figma node IDs and content slots
- `products/registry.json` — **Product packs**: finished, on-brand product slides (Kitchen Station, purifiers) the generator can clone-and-rewrite (see Product Content Library below)
- `assets/library.json` — Brand + product image index (keyed by SEO name → Figma nodeId, tags, description)
- `.claude/commands/generate-presentation.md` — Slash command orchestrating the full pipeline
- `.claude/commands/index-product.md` — Slash command that indexes a finished product deck into `products/registry.json`
- `tools/validate_products.py` — Regression gate for `products/registry.json`
- Figma file: `GkUiwJTK5Xi65AKw4MOjTL` (Bluewater 2026)
- Template page: "Template references" (id: `56881:463`) — single canonical source. ("Templates 4" `50285:14832` is retired.)

## How It Works

1. User provides a PDF
2. Claude reads it, extracts content per slide
3. Claude reads `templates/registry.json` (templates + typography system) and `templates/design-system.md` (grid rules, creative decisions)
4. Claude matches each slide to the best template — or builds from scratch using design system rules when content needs a custom layout
5. Claude generates slides in Figma via `use_figma` MCP tool (clone template → fill text, or build custom bento grids)
6. Output: new page in the Bluewater Figma file

## Design System

- `templates/design-system.md` — Three-layer token system: typescale (Minor Third), card size tiers (xs/sm/lg/hero with fixed sizes), impact overrides (content-triggered exceptions). Also covers grid, bento cards, colors (Gray/Blue/Rose/Green token scales), and creative decision guide.
- `templates/registry.json` — Template registry with `typography` spec and `flexible` metadata per template
- Templates with `flexible.buildFromScratch: true` can be rebuilt with different item counts using the grid system
- Templates with `flexible.optionalSlots` allow hiding unused text elements
- Templates with `flexible.impactSlots` allow scaling up dramatic numbers/phrases

## Template Font

Templates use **Suisse Int'l** (Semi Bold, Medium, Regular). Custom fonts are uploaded to the Figma org under Admin → Resources → Fonts.

## Adding New Templates

1. Design the template in Figma on the "Template references" page, conforming to `slideContract` (48px margins, title 64@y115, body 28, content y287→1032)
2. Use semantic text layer names: `title`, `body`, `bullet-heading-N`, `bullet-body-N`, `cell-heading-N`, `cell-body-N`, etc.; include `meta-left` / `meta-right`
3. Run `auditFrame` (design-system.md) — must pass — then add an entry to `templates/registry.json` with nodeId, slots, and matchHints

## Product Content Library

A **product-aware** layer on top of the generic templates. `products/registry.json` holds **product packs** — finished, on-brand, hand-built product slides the team is happy with, indexed so the generator can reuse them:

- Each product has `aliases` (detection terms), `slides[]` (each with `role`, `nodeId`, `frameName`, `matchHints`, and `slots` = the editable text), a `content` block (verified `valueProps`/`keySpecs`), and `images[]` (`assetKey` refs into `assets/library.json`).
- **Role vocabulary** (controlled, shared): `hero · key-specs · how-it-works · value-prop · comparison · pricing · sustainability · use-case · cta`.
- **Product-first matching**: when a deck mentions a known product, `generate-presentation` checks the product pack *before* generic templates. If a product slide's `role` + `matchHints` fit an incoming slide, it **clones the finished slide and rewrites only the text** (always-rewrite); otherwise it falls back to from-scratch (today's behavior), still preferring product `content` + images. Purely additive — zero product matches → identical behavior to before.
- **Single source of truth**: product slides live only in Figma (registry is a generated mirror); images live only in `assets/library.json` (referenced by `assetKey`, never duplicated).

### Adding a New Product

1. Build the finished product deck in Figma on its own page (any page — node IDs are global).
2. Run `/index-product <slug>` — Claude names the layers semantically, indexes images into `assets/library.json`, proposes `role` + `matchHints` per slide (you confirm), and writes the `products/registry.json` entry.
3. It runs `python3 tools/validate_products.py` — must end `OK`.

## 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately – don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

## 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

## 3. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

## 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

## 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes – don't over-engineer
- Challenge your own work before presenting it

## 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests – then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

# Task Management
1. **Plan First**: Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to `tasks/todo.md`
6. **Capture Lessons**: Update `tasks/lessons.md` after corrections

# Core Principles
- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.
