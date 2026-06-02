# HubSpot Integration Notes (verified spike — 2026-06-02)

Authoritative, **tested** notes for how the email renderer talks to HubSpot.
Everything here was confirmed by live API calls against the Bluewater portal, not
just docs. Where a fact came only from docs it is marked *(docs)*.

## Account

- **Portal ID:** `8076719`
- **Marketing tier:** Marketing Hub **Professional** (currency EUR, TZ America/Vancouver)
- **Consequence:** custom email templates + draft creation work; **publishing/sending
  via API is Enterprise-only** *(docs)* — we never call publish. Drafts only; a human
  sends from the HubSpot UI.

## Auth

- **Mechanism:** Private App access token (NOT a personal access key / `hs` CLI).
- **Private App:** "Bluewater Designer", app id `41456171`.
- **Scopes:** `content` (marketing emails) + `files` (File Manager image hosting).
  - `cms.source_code.*` is **not offered to Private Apps** — so we do NOT upload coded
    templates with this token (see "Template strategy" — we don't need to).
- **Token location:** `~/.hubspot_token`, mode `600`, gitignored. Read it, send as
  `Authorization: Bearer <token>`. Same convention as `~/.figma_token` / `~/.voyage_token`.
- **Verified:** `GET /marketing/v3/emails/?limit=1` → `200` (288 emails). Before the
  `content` scope it returned `403 MISSING_SCOPES → requires "content"`.

## Template strategy — clone-and-rewrite (KEY FINDING)

The existing Bluewater newsletters are **drag-and-drop (DnD) emails**, not coded
templates. Inspecting a real one (`Bluewater Dealers "Where to Buy" update`,
id `35055717485`):

- `emailTemplateMode`: `DRAG_AND_DROP`
- `content.templatePath`: `@hubspot/email/dnd/welcome.html` (a HubSpot default DnD shell)
- `content.widgets`: the editable **modules = our "slots"**
- `content.styleSettings`: brand look — fonts (incl. the Helvetica fallback), colors, sizes
- `content.flexAreas`: layout regions (e.g. `main`)

**Therefore we do NOT build/upload a custom coded template.** We **clone an existing
on-brand email's `content` and rewrite the widget bodies per product** — the same
clone-and-rewrite pattern the Figma product packs use. This sidesteps the
`cms.source_code` scope gap entirely.

### Slot (widget) mechanics — verified by reading a live email

| Slot type | `body.path` | Set this field | Holds |
|---|---|---|---|
| Rich text | `@hubspot/rich_text` | `body.html` | headline / body copy (HTML string) |
| Image | `@hubspot/image_email` | `body.img` | product image (hosted URL — see Images) |
| Preview text | (type `text`, name `preview_text`) | `body.value` | inbox preview line |

`content.styleSettings` keys seen: `backgroundColor`, `bodyColor`, `primaryFont`,
`primaryFontColor`, `primaryFontSize`, `headingOneFont`, `headingTwoFont`, `linksFont`,
`secondaryFont`, `buttonStyleSettings`, `dividerStyleSettings`, … → this is where the
Helvetica stack + Gray/Blue brand colors get pinned.

## Create a draft — verified

`POST https://api.hubapi.com/marketing/emails/2026-03`

```json
{
  "name": "<internal name>",
  "subject": "<subject line>",
  "content": {
    "templatePath": "@hubspot/email/dnd/welcome.html",
    "styleSettings": { "...": "brand fonts/colors" },
    "flexAreas": { "main": { "...": "layout" } },
    "widgets": {
      "preview_text": { "type": "text", "name": "preview_text", "body": { "value": "..." } },
      "module-1-1-1": { "type": "module", "body": { "path": "@hubspot/rich_text", "html": "<h1>...</h1>" } },
      "module-0-1-1": { "type": "module", "body": { "path": "@hubspot/image_email", "img": { "src": "<hosted url>" } } }
    }
  }
}
```

- **Result:** `201 Created`, `state: DRAFT`, `isPublished: false`.
- **Verified artifact:** spike draft id `214131943951`
  (name "ZZ Claude Spike — Hello World (safe to delete)") — a DRAFT, never sent.
  Safe to delete from HubSpot UI (Marketing → Email) or via `DELETE`.
- **Gotcha:** the create path is `/marketing/emails/2026-03` (versioned API),
  NOT `/marketing/v3/emails/2026-03`. Reads use the v3 family
  (`GET /marketing/v3/emails/{id}`). Do not mix them → `405 Method Not Allowed`.

## Recommended production flow for `/generate-newsletter`

1. Read the canonical Bluewater newsletter id from `newsletters/registry.json`.
2. `GET /marketing/v3/emails/{canonicalId}` → take its `content` (templatePath,
   styleSettings, flexAreas, widgets) as the rigid skeleton.
3. Pull the chosen product's verified copy/specs from `products/registry.json`.
4. For each image: upload to File Manager (Files API, `files` scope) → hosted URL.
5. Rewrite widget bodies (rich_text → html, image → img, preview_text → value).
6. `POST /marketing/emails/2026-03` with name + subject + rewritten content → **draft**.
7. Return the draft's edit URL to the user. **Never** call publish/send.

## Images (File Manager)

- Scope `files` confirmed on the token. Upload via the Files API to get a public
  CDN URL, then set it into the image widget's `body.img`. *(upload call not yet
  exercised — first real image upload happens in implementation.)*
