# HubSpot Integration Notes (verified spike — 2026-06-02)

Authoritative, **tested** notes for how the email renderer talks to HubSpot.
Everything here was confirmed by live API calls against the Bluewater portal.
Where a fact came only from docs it is marked *(docs)*.

**Chosen approach: CODED emails** (HTML + HubL templates with named module slots).
Drag-and-drop is possible but rejected — Jens wants full control over the markup.

## Account

- **Portal ID:** `8076719`
- **Marketing tier:** Marketing Hub **Professional** (currency EUR, TZ America/Vancouver)
- **Consequence:** coded templates + draft creation work; **publishing/sending via API
  is Enterprise-only** *(docs)* — we never call publish. Drafts only; a human sends
  from the HubSpot UI.

## Auth — hybrid (two credentials, by necessity)

Coded emails need two scopes that no single Private-App token can hold, so we split:

| Job | Credential | Scope | Frequency |
|---|---|---|---|
| Upload/manage the coded **template** | `hs` CLI / PAK | `cms.source_code.write` | occasional (setup) |
| Create the **draft email** + upload images | Private App token | `content`, `files` | every newsletter |

- **Private App:** "Bluewater Designer", app id `41456171`, scopes `content` + `files`.
  Token at **`~/.hubspot_token`** (mode `600`, gitignored). Send as
  `Authorization: Bearer <token>`. Same convention as `~/.figma_token`.
  - Private Apps are **not** offered `cms.source_code.*` — that's why template upload
    uses the CLI instead.
- **`hs` CLI / PAK:** default account `bluewater` (`8076719`), already authenticated
  (`~/hubspot.config.yml`). Has `cms.source_code.write`.
- **Verified:** `GET /marketing/v3/emails/?limit=1` → `200`. (Before the `content`
  scope: `403 MISSING_SCOPES → requires "content"`.)

## Coded-email pipeline — VERIFIED end-to-end

### 1. Author the coded template (HTML + HubL)

A coded email template declares editable **slots** as named HubL modules:

```hubl
{% module "headline" path="@hubspot/rich_text"
   html="<h1>Default headline</h1>" %}
{% module "hero" path="@hubspot/image_email" %}
```

Required HubSpot email tags (HubSpot enforces at send): `{{ email_header_includes }}`,
`{{ email_footer_includes }}`, `{{ unsubscribe_link }}`, and a physical company
address (CAN-SPAM). Email constraints still apply: 600px, table layout, **Helvetica,
Arial, sans-serif** (no web fonts), inline styles. See `email-design-system.md`.

### 2. Upload it to the Design Manager (CLI / PAK)

```bash
hs cms upload <local.html> bluewater-designer/<name>.html
```

- **Gotcha:** `hs`'s default `.hsignore` skips dot-paths — upload from a NON-dot
  directory (uploading a file under `~/.claude/...` is silently ignored).
- `hs upload` is deprecated → use `hs cms upload`.
- **Verified:** uploaded `bluewater-designer/spike-hello-world.html` → SUCCESS.

### 3. Create a DRAFT from it, filling slots (Private App token)

`POST https://api.hubapi.com/marketing/emails/2026-03`

```json
{
  "name": "<internal name>",
  "subject": "<subject line>",
  "content": {
    "templatePath": "bluewater-designer/<name>.html",
    "widgets": {
      "headline": { "type": "module",
        "body": { "path": "@hubspot/rich_text", "html": "<h1>...product copy...</h1>" } },
      "hero": { "type": "module",
        "body": { "path": "@hubspot/image_email", "img": { "src": "<File-Manager URL>" } } }
    }
  }
}
```

- **Result:** `201 Created`, `state: DRAFT`, `isPublished: false`,
  `emailTemplateMode: DESIGN_MANAGER`.
- **Slot fill = override:** a template module renders its in-template default UNTIL you
  set `content.widgets["<moduleName>"]`. Setting it overrides that slot.
  **Verified:** overriding `headline.body.html` persisted on a follow-up GET.
- **Gotcha:** create path is `/marketing/emails/2026-03` (versioned API), NOT
  `/marketing/v3/emails/2026-03` → `405`. Reads use v3: `GET /marketing/v3/emails/{id}`.

### Slot type → field cheat sheet (verified by reading live emails)

| Slot kind | module `path` | set field | holds |
|---|---|---|---|
| Rich text | `@hubspot/rich_text` | `body.html` | headline / body copy (HTML) |
| Image | `@hubspot/image_email` | `body.img.src` | product image (hosted URL) |
| Preview text | type `text`, name `preview_text` | `body.value` | inbox preview line |

## Production flow for `/generate-newsletter`

1. Read the coded template's path + slot inventory from `newsletters/registry.json`.
2. Pull the chosen product's verified copy/specs from `products/registry.json`.
3. For each image: upload to File Manager (Files API, `files` scope) → hosted URL.
4. `POST /marketing/emails/2026-03` with name + subject + `content.templatePath` +
   `content.widgets` (one entry per slot to fill) → **draft**.
5. Return the draft's edit URL to the user. **Never** publish/send.

(Template changes are an occasional, separate `hs cms upload` step — surfaced via
`/index-newsletter`, not `/generate-newsletter`.)

## Images (File Manager)

Scope `files` confirmed on the token. Upload via the Files API to get a public CDN URL,
then set it into the image module's `body.img.src`. *(First real upload happens during
implementation — not yet exercised.)*

## Spike artifacts to clean up (production portal)

Created during this spike, all DRAFT / never sent — safe to delete:
- Draft `214131943951` — "ZZ Claude Spike — Hello World" (DnD)
- Draft `214131944010` — "ZZ Claude Spike — CODED template"
- Draft `214131940962` — "ZZ Claude Spike — coded + slot override"
- Design Manager file `bluewater-designer/spike-hello-world.html`
