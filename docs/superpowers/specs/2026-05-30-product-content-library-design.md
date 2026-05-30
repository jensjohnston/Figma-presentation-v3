# Product Content Library — Design Spec

**Date:** 2026-05-30
**Status:** Approved design, pending implementation plan
**Author:** Jens + Claude (brainstorming session)

## Problem

The generator today rebuilds every slide from scratch using product-agnostic
layouts (`templates/registry.json`, 69 generic shells) plus design tokens. It has
no awareness of the *finished, polished, product-specific* slides the team has
already built and is happy with (e.g. Kitchen Station, the purifier set).

When a new presentation mentions a product, the generator should be able to
**reach for that product's existing finished content** — finished slides, verified
copy, and specific product images — instead of reinventing it every time.

## Goal

Add a **product-aware content layer** on top of the existing generator so that,
when a deck mentions a known product, the generator can:

1. **Reuse a finished product slide** (clone it, rewrite the text)
2. **Pull verified content** (specs, value props, pricing) into any layout
3. **Place a specific product image** anywhere it builds

This is **purely additive**. It does not modify the existing from-scratch path —
that remains the fallback. If no product is detected or no slide fits, the
generator behaves exactly as it does today.

## Non-Goals

- Not changing the design system, typography, grid, or chrome rules.
- Not changing how generic templates are matched or filled.
- Not building a runtime/build step — Claude remains the engine.
- Not auto-presenting product decks (a product page being presentable directly is
  a nice side effect, not a feature we build).

## Key Decisions (from brainstorming)

| # | Decision | Choice |
|---|----------|--------|
| 1 | Reusable unit | **Product pack**: finished slides + content blocks + image references |
| 2 | Figma organization | **Per-product page** is the destination; current shared page is a fine on-ramp. Page location is invisible to the generator (it reads node IDs from the registry), so this is a human-ergonomics choice with no technical impact. |
| 3 | Decision model | **Product-first**: product slide wins if it fits; build-from-scratch is the fallback. |
| 4 | Slide labeling | **Role + matchHints** (mirrors the template registry's structured-slots + free-text pattern). Role is the backbone + coverage map; matchHints handles judgment calls. |
| 5 | Images | **Referenced** from `assets/library.json`, never duplicated in the product pack. |
| 6 | Text behavior | **5a — always rewrite.** Product slides are polished *shells*; each deck's words flow in. Verified `content` blocks are the source when the PDF is thin. |
| 7 | Authoring | **Claude-driven `/index-product <slug>` command** generates the registry entry from what was built in Figma — not hand-authored. |

## Data Model

New file: **`products/registry.json`** (mirrors `templates/registry.json` so it is
familiar). Keyed by product slug.

```jsonc
{
  "fileKey": "GkUiwJTK5Xi65AKw4MOjTL",
  "products": {
    "kitchen-station": {
      "displayName": "Kitchen Station",
      "pageId": "56881:463",              // where its slides currently live
      "aliases": ["kitchen station", "kitchen-station", "kitchenstation"],
      "slides": [
        {
          "role": "hero",
          "nodeId": "...",
          "matchHints": "Opening/product-intro slide for Kitchen Station.",
          "slots": { "title": "...", "body": "..." }
        },
        {
          "role": "key-specs",
          "nodeId": "...",
          "matchHints": "Technical specifications / what's in the box.",
          "slots": { "...": "..." }
        }
      ],
      "content": {
        "keySpecs": ["..."],
        "valueProps": ["..."],
        "pricing": { "...": "..." }
      },
      "images": [
        { "assetKey": "kitchen-station-hero" }   // -> resolves in assets/library.json
      ]
    }
  }
}
```

Design choices baked in:
- **Images are references** (`assetKey`) into `assets/library.json` — one home, no
  duplication. The asset library already tags by product (e.g. `cafe-station-1-hero`
  → `["product","cafe-station","hero"]`), so this extends an existing pattern.
- **`aliases`** is the detection key — the generator scans PDF text for any alias to
  decide which product(s) the deck is about.
- **`slots`** uses the same semantic layer-name convention as templates (`title`,
  `body`, `cell-heading-N`, …) so the generator knows exactly what to rewrite.

### Role vocabulary (shared, controlled, extensible)

```
hero · key-specs · how-it-works · value-prop · comparison ·
pricing · sustainability · use-case · cta
```

One shared vocabulary across all products so a role never drifts
(`specs` vs `specifications`). Extend the list when a product genuinely needs a new
role; never fork synonyms.

## Generation Flow

Steps in **bold** are new; the rest is today's pipeline unchanged.

1. Read PDF, extract content per slide.
2. **Detect products** — scan deck text against every product's `aliases`. Yields
   zero, one, or several matched products.
3. Read `templates/registry.json` + `design-system.md`.
4. **Load matched product packs** — slides, content, image references.
5. For each incoming slide, **product-first match**:
   - Is there a product slide whose `role` + `matchHints` fit this slide's intent?
     → **clone the finished product slide, rewrite the text** (slots filled from the
       incoming PDF; verified `content` used where the PDF is thin). *(decision 5a)*
   - No fit? → build from scratch with generic layouts (today's behavior), but still
     **prefer product `content` + product images** when filling.
6. Generate in Figma (unchanged mechanism).

**Matching note:** product-first means that for a given incoming slide, the generator
checks the product pack *before* deciding it needs a generic layout. Role provides the
coarse filter (does the deck's intent map to a role we have?), matchHints resolves
the fine call. Ties and ambiguity resolve toward reusing the product slide.

## Authoring Workflow (`/index-product`)

Mirrors the existing "Adding New Templates" process. The team designs in Figma; the
registry is generated *from* what they built.

1. **Build** finished product slides in Figma on the product's page.
2. **Name layers semantically** (`title`, `body`, `cell-heading-N`, …) so slots are
   discoverable — same convention as templates.
3. **Run `/index-product <slug>`** — Claude:
   - reads the product's slides from Figma,
   - auto-suggests `role` + `matchHints` + `slots` per slide (user confirms/tweaks),
   - extracts images, adds them to `assets/library.json` with SEO-friendly,
     content-descriptive names (per the existing image-naming rule),
   - writes/updates the product entry in `products/registry.json`.

The registry is thus a *generated index*, in the same spirit as `auditFrame` for
templates — the source of truth is the Figma page; the registry mirrors it.

## Integration Points

| File | Change |
|------|--------|
| `products/registry.json` | **New.** Product packs index. |
| `assets/library.json` | Extended — product images get indexed here by `/index-product`. |
| `.claude/commands/generate-presentation.md` | Add steps 2, 4, 5 (detect → load → product-first match). The from-scratch path is unchanged and remains the fallback. |
| `.claude/commands/index-product.md` | **New.** The authoring command. |
| `CLAUDE.md` | Document the product layer + `/index-product` alongside "Adding New Templates". |

## Risk / Safety

- **Additive only.** No change to the from-scratch path. Zero product matches →
  identical behavior to today.
- **Single source of truth per layer.** Images live only in `assets/library.json`;
  product slides live only in Figma (registry is a generated mirror). Avoids the
  divergent-source-of-truth class of bug noted in `tasks/lessons.md` (the Templates-4
  stale-geometry incident).
- **Node IDs survive page moves**, so migrating a product to its own page later is a
  one-field registry change (`pageId`), not a re-index.

## Open Questions (defer to implementation plan)

- Exact confidence threshold for "does this product slide fit this incoming slide"
  — start simple (role match + matchHints judgement), tune if needed.
- Whether `/index-product` should run an `auditFrame`-style contract check on product
  slides before indexing (likely yes, reusing the existing slide contract).
- Multi-product decks: ordering/precedence when two products are detected (start:
  match each slide independently to whichever product fits best).
