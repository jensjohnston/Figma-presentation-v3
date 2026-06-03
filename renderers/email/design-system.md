# Bluewater Email Design System

The on-brand system for HubSpot product newsletters — the email-medium counterpart to
`templates/design-system.md` (Figma slides). **Reverse-engineered from the reference email
the team is happy with:** "Kitchen Station 1 — Marketing email" (HubSpot id `187950269215`,
portal `8076719`). That email is the canonical visual target for logo, type, color, and spacing.

Every value below is mapped to a token in `core/brand-tokens.json` so the email and Figma
renderers stay one brand. Email font is always **Helvetica, Arial, sans-serif** (no web
fonts — Suisse Int'l is Figma-only).

---

## 1. Canvas & frame

| Property | Value | Token / note |
|---|---|---|
| Page background | `#FAFAFA` | gray/50 |
| Content background | `#FFFFFF` | gray/white |
| Content width | **600px** boxed, **552px** live image width → **24px** side padding | email standard |
| Content border | `#EAF0F6` 1px | HubSpot default (≈ gray/100 `#F4F4F5`) — **see improvement #4** |
| Section divider rule | `#E4E4E7`, 1px solid, 100% | gray/200 |

Single column throughout. No multi-column rows — feature content is **stacked** (image on
top, text below), which is the safest pattern across email clients.

---

## 2. Logo header

- Asset: **`Bluewater_Logo_Horizontal_Black_RGB`** (black horizontal wordmark) on white.
- Rendered **110 × 20px**, centered, linked to `https://www.bluewatergroup.com/`.
- Wrapped top and bottom by a 1px `#E4E4E7` divider rule (creates a clean masthead band).
- Hosted in HubSpot File Manager:
  `…/hubfs/8076719/Bluewater_Logo_Horizontal_Black_RGB.jpg`.

> This is the **real logo** — the current coded template (`product-newsletter.html`) ships a
> text wordmark placeholder. Aligning to this is improvement #1.

---

## 3. Typography

Family: `Helvetica, Arial, sans-serif` (`fontStacks.email`). One ramp, three roles:

| Role | Size / line-height | Align | Color | Token |
|---|---|---|---|---|
| **Hero headline** | 37px / 115% | center | `#000000` | true black |
| **Section / feature headline** | 30px / 115% | left | `#18181B` | gray/900 |
| **Body** | 16px / 145% **semibold (600)** | left | `#71717A` | gray/500 |
| **Body lead sentence** | 16px / 145% **bold** | left | `#71717A` | gray/500, `<strong>` |
| **Button label** | 16px **bold** | — | `#FFFFFF` | white |
| **Footer** | 12px | center | `#23496D` | HubSpot default — **see improvement #4** |

Notes
- Hero uses pure black `#000000`; sections use near-black `#18181B`. Two different "blacks"
  — **harmonize to one** (improvement #2).
- Body is `gray/500` (`#71717A`) here — lighter than the current engine's intro color
  `gray/600` (`#52525B`). The reference (lighter) wins; reconcile the engine to it.
- Lead sentences are set bold to open a feature, then semibold for the explanation.
- **Body weight is semibold (`font-weight:600`)**, not regular — applied to intro, feature body,
  and the spec-grid continuation, so the weight is visible even on web-safe Arial/Helvetica.
  Headings and `<strong>` leads remain bold (700). Controlled by `BODY_WEIGHT` in `hs_newsletter.py`.
- **Headlines end with a period.** The hero headline and every feature headline end in a full stop
  (brand rule) — unless they already end in terminal punctuation (e.g. a question, "…Safe?").
  Enforced in code by `_ensure_dot()` in `hs_newsletter.py`, so registry copy needn't include the dot.

---

## 4. Color palette (as used)

| Use | Hex | Token |
|---|---|---|
| Hero headline | `#000000` | black |
| Section headline | `#18181B` | gray/900 |
| Body copy | `#71717A` | gray/500 |
| Button fill | `#2563EB` | **blue/600** |
| Button label | `#FFFFFF` | white |
| Divider rule | `#E4E4E7` | gray/200 |
| Page bg | `#FAFAFA` | gray/50 |
| Content bg | `#FFFFFF` | white |

**Brand-token gaps to resolve (improvement #4):**
- Footer link `#00A4BD` (teal) and footer text `#23496D` are **HubSpot stock defaults**, not
  Bluewater tokens — they slipped through unedited.
- The button is **blue/600 `#2563EB`**, but Bluewater's primary brand color is
  **navy blue/950 `#00205B`**. The reference is not using brand navy anywhere. This is the
  single biggest brand decision to make (see "Open decision" below).

---

## 5. Components

### 5.1 Feature row (the workhorse — repeated 4× in the reference)

Stacked, single column, in this exact order:

```
[ Image            552px wide, full content width, linked to product page ]
[ Headline         30px / 115% / left / gray-900                          ]
[ Body             16px / 145% / left / gray-500 (lead sentence bold)     ]
[ Button  "Learn more"  pill, blue-600, 25px radius, white bold 16px      ]
```

- **Button** = `@hubspot/button_email`: fill `#2563EB`, corner radius **25px** (full pill),
  label bold white 16px, **left**-aligned, wrapper padding `0 / 20px / 48px / 20px`
  (top/right/bottom/left) — the 48px bottom is the gap to the next feature row.
- Images carry the product-page link too (whole-image click target).

The reference stacks four of these: *Is Your Tap Water Safe?* · *Purified and Remineralised
Water* · *Bluewater O* · *Bluewater App* — i.e. a **multi-feature product showcase**, not a
single-spec card.

### 5.2 Masthead — see §2.

### 5.3 Hero — centered headline only (37px black), directly above the first feature row.

### 5.4 Spec grid (Apple-Watch style) — `specs` slot, engine-built, optional

A **2-up grid of compact spec items**, placed below the feature rows. Each item is a thin
divider rule (`#E4E4E7`, 1px) **above**, then a one-line **bold lead + muted continuation**:

```
───────────────              ───────────────
SuperiorOsmosis™             Liquid Rock®
purification.  Removes       minerals.  A 2:1 Ca:Mg
contaminants to the          electrolyte blend from
molecular level.             Sweden's bedrock.
```

- Cell: `border-top:1px solid #E4E4E7`, 16px gap to text, **28px** below, 15px / 145%.
- **Lead** = `<strong>` gray/900 `#18181B`; **continuation** = gray/500 `#71717A` (same line).
- Two columns at 50% with a 24px channel; **stack to one column** under 480px (`.bw-grid-cell`).
- Odd item counts keep a balanced empty cell. Source: `specs: [{heading, body}, …]` in the pack.
- Use for scannable key specs/benefits *after* the narrative feature rows — not a replacement
  for them.

### 5.5 Footer — `@hubspot/email_footer`, centered 12px, unsubscribe (both list + all),
CAN-SPAM compliant (name + street + city + **state**), 20px top/bottom padding.

---

## 6. Spacing

- Side gutters: **24px** (600 − 552 ÷ 2).
- Between feature rows: **48px** (button wrapper bottom padding).
- Masthead: bracketed by 1px dividers, no extra vertical padding.
- Footer block: **20px** top and bottom.
- Most DnD sections run `padding: 0` and lean on module-default spacing + line-height — so
  rhythm is **inconsistent by section**. A coded template should make the 48px row gap
  explicit and uniform (improvement #3).

---

## 7. How this maps to the coded renderer

The reference is a **drag-and-drop** email (`@hubspot/email/dnd/Start_from_scratch.html`).
Our pipeline uses a **coded** template (`renderers/email/templates/product-newsletter.html`)
so the team gets the same look every time, version-controlled, with named slots. To reach
parity, the coded template needs to grow from "single hero + 3 stacked specs + 1 button" to
support a **logo masthead + centered hero + N feature rows** (image · headline · body ·
button). That is the substance of the improvements below.

---

## 8. Improvements — adopted in v2 (2026-06-03)

All of the following are now live in `product-newsletter.html` + `hs_newsletter.py`:

1. ✅ **Real logo** in the masthead (hosted `Bluewater_Logo_Horizontal_Black_RGB`, divider-bracketed).
2. ✅ **One ink** — `#18181B` (gray/900) for hero + feature headlines; no stray pure-black.
3. ✅ **Explicit rhythm** — 24px gutters + 48px inter-feature gap baked into the coded template.
4. ✅ **Brand-token footer** — links recolored to blue/600 `#2563EB`; HubSpot stock teal removed.
5. ✅ **Feature row is a component** — engine-built from `features[]`, any count (2–5).
6. ✅ **Body color** reconciled to gray/500 `#71717A`.
7. ✅ **Spec grid added** (§5.4) — the Apple-style 2-up key-specs block.
8. ◻️ **Accessibility:** images now carry `alt` (defaults to the feature headline). Dark-mode
   hardening is partial — see the Emergency variant note below.

### Resolved — accent color
**Locked: blue/600 `#2563EB`** is the canonical email accent (buttons + links), per Jens
(2026-06-03). It matches the approved reference; brand navy `#00205B` stays the slide accent.

---

## 9. Coverage & variants

**This is THE template for all Bluewater product emails / newsletters.** Every product email
is produced by `/generate-newsletter <slug>` against `product-newsletter.html`; the only
variation between products is the slot content (hero headline, features, specs, images).

### Variant — Emergency Station (inverted / dark) — BUILT 2026-06-03
Emergency Station emails invert the palette via the `dark` theme:

| Role | Light | Dark |
|---|---|---|
| Content bg | `#FFFFFF` | gray/950 `#09090B` (page `#000000`) |
| Heading / ink | gray/900 `#18181B` | gray/50 `#FAFAFA` |
| Body | gray/500 `#71717A` | gray/400 `#A1A1AA` |
| Spec divider | gray/200 `#E4E4E7` | gray/700 `#3F3F46` |
| Button | blue/600 `#2563EB` | blue/600 `#2563EB` (reads on dark) |
| Footer links | blue/600 | blue/400 `#60A5FA` |

Same structure (masthead, hero, feature rows, spec grid, footer) — only the tokens flip.
- Template: `renderers/email/templates/product-newsletter-dark.html` (uploaded as
  `bluewater-designer/product-newsletter-dark.html`); the light template is untouched.
- A pack opts in with `"variant": "dark"`; the engine then picks `hubspot.templatePathDark`
  and the dark color theme. Default (no `variant`) stays light.
- **Logo:** the dark masthead uses a **reverse/white Bluewater logo**, divider-bracketed (gray/800
  `#27272A`), on the dark body. The white logo was derived from the black source (luminance → alpha,
  transparent PNG) and hosted at
  `…/hubfs/8076719/bluewater-designer/Bluewater_Logo_Horizontal_White_RGB.png`.
