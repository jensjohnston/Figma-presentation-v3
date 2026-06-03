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
source: `renderers/email/templates/product-newsletter.html`). It renders a **logo masthead
→ centered hero headline → optional intro → a stack of N feature rows → footer** (the system
is documented in `renderers/email/design-system.md`, reverse-engineered from the approved
reference email). Named module slots (`hero_headline · intro · features`) are filled by
overriding `content.widgets`; the `features` stack is built by the engine from the pack's
`features[]`. The deterministic plumbing (Figma image → File Manager → create draft) is
`tools/hs_newsletter.py`. See `renderers/email/HUBSPOT-INTEGRATION.md`.

Auth is already configured: `~/.hubspot_token` (Private App) + `~/.figma_token`.

## Steps

1. **Read the slug.** Resolve `<product-slug>` against `renderers/email/newsletters/registry.json`.

2. **If a newsletter pack already exists** for the slug → skip to step 4.

3. **If it does NOT exist, compose one (clone-and-rewrite):**
   - Read the product from `products/registry.json` (verified `content`: valueProps,
     keySpecs, and slide slots) — this is the source of truth for copy. Do **not** invent specs.
   - Map content to the pack shape, honoring brand voice (title case, never ALL CAPS):
     - `heroHeadline`: a short, benefit-led campaign line (e.g. "Clean Water, On Demand").
     - `intro` (optional): one lead-in sentence under the hero; omit to skip.
     - `features[]`: **2–5** feature rows, each `{ image, headline, body, ctaLabel }`.
       - `image`: an assetKey from `assets/library.json` whose `tags` include the product
         (prefer hero/lifestyle for the first row, then components). May also be a direct
         https URL for art already hosted (e.g. an animated GIF Figma can't render).
       - `headline`: the feature name (bind single-word widows with `&nbsp;` if needed). Headlines
       end with a period (brand rule) — but the engine appends it via `_ensure_dot()`, so don't
       hand-add dots in the registry (and `?`/`!` endings are left as-is).
       - `body`: 1–2 sentences from a value prop / component; a bold `<strong>` lead is OK.
       - `ctaLabel`: e.g. "Learn more". Set top-level `ctaUrl` to the product page
         (default `https://www.bluewatergroup.com` if unknown — confirm with the user);
         a feature may override with its own `ctaUrl`.
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
