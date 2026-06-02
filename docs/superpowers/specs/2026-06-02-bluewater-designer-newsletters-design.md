# Bluewater Designer — Newsletter Renderer (HubSpot)

**Date:** 2026-06-02
**Status:** Approved design, pending implementation plan
**Branch:** `feature/newsletter-designer`

## 1. Goal

Turn this repo from a *Figma presentation generator* into **the Bluewater Designer**:
one shared brand/content core feeding multiple output *renderers*. Today's renderer
emits Figma slides. This project adds a second renderer that emits **live, sendable
HubSpot marketing emails** (product newsletters).

A newsletter is product-driven and rigid: a fixed template (spacing, headline scale,
section order) into which a single product's verified copy/specs/images are swapped —
the email-world equivalent of a Figma template + the product content library.

## 2. Decision: one repo, not two

Keep everything in **one repo**. The deciding factor is reuse of the product content
library (`products/registry.json`) and image index (`assets/library.json`). A product
newsletter and a product slide must pull from the *same verified facts*. A separate repo
would force duplication (drift) or a sync mechanism (complexity) — both discard the prize.

Rejected alternatives:
- **Full monorepo refactor now** — churns a working system for outputs not yet built (YAGNI).
- **Separate repo** — contradicts the "one core, many outputs" vision; loses library reuse.

## 3. Architecture

Reorganize around *brand truth* vs *renderer*. Presentation behavior is unchanged; we are
naming a seam that already exists implicitly.

```
core/                          ← medium-agnostic brand truth (shared)
  brand-tokens.json              colors (Gray/Blue/Rose/Green scales), typescale ratios,
                                 per-medium font stacks (Figma: Suisse Int'l;
                                 Email: Helvetica, Arial, sans-serif)
  voice.md                       copy voice/tone rules
products/registry.json         ← shared by BOTH renderers (verified content + images)
assets/library.json            ← shared; gains a hosted public URL per asset (for email)

renderers/
  figma/                       ← today's system, behavior unchanged
    templates/registry.json
    design-system.md
    (generate-presentation command)
  email/                       ← NEW
    newsletters/registry.json    mirror of the rigid HubSpot email template's slots
    email-design-system.md       email-specific rules (see §5)
    (generate-newsletter command)
    (index-newsletter command — keeps registry a mirror of HubSpot truth)
```

**Shared vs medium-specific (the core distinction):**
- **Shared (in `core/` + product/asset libraries):** colors, typescale *ratios*, product
  facts (valueProps/keySpecs/pricing), image *content*, copy voice.
- **Figma-only:** bento grid, card size tiers (px), `slideContract`, node IDs, line-height
  as Figma PERCENT units, Suisse Int'l, display sizes up to 96px.
- **Email-only:** single-column ~600px, table layout, Helvetica fallback, inline styles,
  hosted image URLs, CAN-SPAM footer, smaller headline scale (see §5).

## 4. Workflow: how a newsletter is made

Mirrors the product-pack philosophy: *canonical template lives in HubSpot; repo holds a
mirror; clone-and-fill via API.*

1. `/generate-newsletter <product-slug>` (e.g. `kitchen-station`).
2. Read the rigid template's slots from `renderers/email/newsletters/registry.json`.
3. Pull the product's verified `content` + `images` from the shared product library.
4. Fill slots (headline, body, key specs, CTA, product image) within the **fixed** spacing/
   structure system — rigidity enforced here (the email equivalent of `slideContract`).
5. Render HTML+HubL and create a **DRAFT** marketing email in HubSpot via API.
   **Never auto-send** — Jens reviews and sends from HubSpot.

## 5. Email rendering constraints (locked in up front)

Email is not a small slide. These rules live in `email-design-system.md` and are
non-negotiable for reliable cross-client rendering:

- **Fonts:** No custom/web fonts. Suisse Int'l → **`font-family: Helvetica, Arial,
  sans-serif`**. Outlook strips web fonts; Helvetica is the chosen fallback.
- **Layout:** Single column, **max ~600px** wide. **Table-based** layout only —
  no flexbox/grid (Outlook uses Word's rendering engine).
- **Styles:** Inline styles on elements; do not rely on `<style>` blocks or external CSS
  (many clients strip them). HubL coded email template.
- **Type scale:** Shared *ratios*, but email-appropriate absolute sizes. A 64px slide
  title is wrong in a 600px email — email H1 ≈ 28–32px, body ≈ 14–16px (mobile legibility
  floor), line-height unitless/px (not Figma PERCENT).
- **Images:** Absolute **hosted URLs** + meaningful `alt` text. Images are often blocked
  by default — never put critical copy inside an image. Background images are unreliable
  (Outlook) → prefer solid brand-color fills.
- **Buttons:** Bulletproof table-based buttons, not `<button>`.
- **Compliance:** HubSpot enforces a CAN-SPAM footer (physical address + unsubscribe);
  the template must include the HubSpot email footer module.
- **Dark mode:** Some clients invert colors; ensure logos/icons read on inverted backgrounds.

These differences are *why* email is its own renderer and not a variant of the slide system.

## 6. Build order (incremental, each step usable)

- **Step 0 — Reorg (safe):** introduce `core/`, relocate shared references, update the
  presentation command's paths. **Verify presentations still generate identically.** No new
  features. Protects the working pipeline before anything new is added.
- **Step 1 — HubSpot spike:** run `hs account auth` (the HubSpot dev MCP currently errors
  with "No account ID found" — auth is a prerequisite). Confirm the exact API to (a) create
  a coded email template and (b) create a **draft** marketing email from it. Smallest
  possible "hello world" draft pushed to HubSpot.
- **Step 2 — Rigidify the template together:** take Jens's existing loose HubSpot template,
  codify the fixed system (spacing, headline scale, section order, Helvetica stack) into
  `email-design-system.md` + a coded template with **named module slots**.
- **Step 3 — `/generate-newsletter`:** fill slots from a product, push a draft. Add an
  `/index-newsletter` mirror step (analogous to `/index-product`) so the registry stays a
  generated mirror of the HubSpot truth.
- **Step 4 — Validator:** `tools/validate_newsletters.py` gate mirroring
  `tools/validate_products.py` (must end `OK`).

## 7. Open questions / risks

- **Exact HubSpot API surface** for coded email template + draft email creation is
  confirmed in Step 1 (spike) before committing the command design. The HubSpot dev MCP
  (`mcp__HubSpotDev__*`) is the developer/Design-Manager surface; the OAuth CRM connection
  is separate and analytics-focused.
- **Image hosting:** assets need public URLs for email. Decide host (HubSpot file manager
  vs existing CDN) during Step 1–2; add the URL field to `assets/library.json` then.
- **Reorg path updates:** Step 0 must catch every path reference in the presentation
  command/registries; verification is mandatory before proceeding.

## 8. Out of scope (for now)

- Topic-to-draft copywriting (input is product-driven, not theme-driven).
- Auto-send / scheduling (drafts only; human sends).
- Non-product newsletters (announcements, roundups).
- Other future renderers (social, one-pagers) — the core makes them possible, not built.
- PowerPoint export (tracked separately as a presentation Phase 2 item).
