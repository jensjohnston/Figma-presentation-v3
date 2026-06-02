---
description: Generate an on-brand HubSpot product newsletter (draft) from a product
---

# /generate-newsletter <product-slug>

Produce a finished, on-brand **draft** marketing email in HubSpot for a product, by
cloning-and-rewriting the rigid Bluewater newsletter template. **Draft only — never
publish or send.** A human reviews and sends from HubSpot.

Argument: `$ARGUMENTS` (a product slug, e.g. `kitchen-station`). If empty, ask which product.

## How it works

The rigid template lives in HubSpot (`bluewater-designer/product-newsletter.html`,
source: `renderers/email/templates/product-newsletter.html`). Its named module slots
(`hero_image · eyebrow · headline · intro · spec_1 · spec_2 · spec_3 · cta`) are filled
by overriding `content.widgets`. The deterministic plumbing (Figma image → File Manager
→ create draft) is `tools/hs_newsletter.py`. See `renderers/email/HUBSPOT-INTEGRATION.md`.

Auth is already configured: `~/.hubspot_token` (Private App) + `~/.figma_token`.

## Steps

1. **Read the slug.** Resolve `<product-slug>` against `renderers/email/newsletters/registry.json`.

2. **If a newsletter pack already exists** for the slug → skip to step 4.

3. **If it does NOT exist, compose one (clone-and-rewrite):**
   - Read the product from `products/registry.json` (verified `content`: valueProps,
     keySpecs, and slide slots) — this is the source of truth for copy. Do **not** invent specs.
   - Pick a `heroAsset` from `assets/library.json`: an asset whose `tags` include the
     product and `hero`/`lifestyle` (prefer a clean front-facing or lifestyle hero).
   - Map content to slots, honoring the brand voice and the **title-case eyebrow** rule
     (never ALL CAPS):
     - `eyebrow`: a short kicker, e.g. "New from Bluewater" (title case).
     - `headline`: the product display name (bind single-word widows with `&nbsp;` if needed).
     - `intro`: 1–2 sentences from the product's strongest value prop.
     - `spec_1/2/3`: three `{ "heading", "body" }` pairs from keySpecs / how-it-works.
     - `cta`: a button label, e.g. "Explore <Product>". Set `ctaUrl` to the product page
       (default `https://www.bluewatergroup.com` if unknown — confirm with the user).
     - `subject` + `previewText`: benefit-led, no ALL CAPS, no spammy punctuation.
   - Add the entry under `newsletters.<slug>` in
     `renderers/email/newsletters/registry.json` (match the existing shape exactly).
   - Run `python3 tools/validate_newsletters.py` — must print `OK`. Fix any errors.

4. **Generate the draft:**
   ```
   python3 tools/hs_newsletter.py generate --slug <slug>
   ```
   This renders the hero from Figma, hosts it in File Manager, and creates the draft.
   It prints a JSON line with `id`, `state` (must be `DRAFT`), and `editorUrl`.

5. **Report back** the `editorUrl` and confirm it is a DRAFT. Remind the user to review
   and send from HubSpot. **Do not call any publish/send endpoint.**

## Notes
- Purely additive and product-first, mirroring `/generate-presentation`: zero changes to
  the Figma pipeline.
- Re-running for an existing slug creates a fresh draft each time (safe — drafts only).
- Template changes are a separate concern — edit
  `renderers/email/templates/product-newsletter.html` and re-upload via
  `hs cms upload`, surfaced through `/index-newsletter` (not here).
