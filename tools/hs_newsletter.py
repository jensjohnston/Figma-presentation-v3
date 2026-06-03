#!/usr/bin/env python3
"""Bluewater newsletter engine — the deterministic HubSpot/Figma plumbing behind
the /generate-newsletter command.

Two subcommands (Claude composes the slot copy; this script does the mechanical work):

  upload-image  --node <figmaNodeId> --name <slug>
      Render a Figma node to PNG and upload it to the HubSpot File Manager.
      Prints the public CDN url on the last line.

  create-draft  --payload <path-to-json>
      Create (or update) a DRAFT marketing email from a coded template + slot widgets.
      payload JSON: { "name", "subject", "templatePath", "widgets": {slot: html, ...},
                      optional "emailId" to update an existing draft }
      A widget value may be a raw HTML string (rich_text slot) — it is wrapped as a
      @hubspot/rich_text module override. Prints the editor url + email id.

Auth (same convention as the rest of the repo):
  ~/.hubspot_token  — HubSpot Private App token (scopes: content, files)   [mode 600]
  ~/.figma_token    — Figma PAT                                            [mode 600]

NEVER publishes/sends — drafts only. Publishing is Enterprise-only and out of scope.
Verified end-to-end 2026-06-02 (see renderers/email/HUBSPOT-INTEGRATION.md).
"""
import argparse, json, os, sys, urllib.parse, urllib.request, urllib.error, uuid

PORTAL_ID = "8076719"
FILE_KEY = "GkUiwJTK5Xi65AKw4MOjTL"   # Bluewater 2026 Figma file
FILES_FOLDER = "/bluewater-designer/newsletters"
CREATE_URL = "https://api.hubapi.com/marketing/emails/2026-03"   # NOT /marketing/v3/...
V3 = "https://api.hubapi.com/marketing/v3/emails"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Brand tokens (mirror of core/brand-tokens.json — email font stack + key colors).
# See renderers/email/design-system.md (reverse-engineered from reference email 187950269215).
FF = "Helvetica,Arial,sans-serif"
ACCENT = "#2563EB"   # blue/600 — buttons + links (canonical email accent, both themes)
BODY_WEIGHT = "600"  # body copy is semibold (Jens's call — guarantees visible weight on Arial/Helvetica)

# Per-variant color themes. light = default; dark = Emergency Station (inverted).
THEMES = {
    "light": {"ink": "#18181B", "body": "#71717A", "divider": "#E4E4E7"},  # gray 900/500/200
    "dark":  {"ink": "#FAFAFA", "body": "#A1A1AA", "divider": "#3F3F46"},  # gray 50/400/700
}


def _read_token(path):
    p = os.path.expanduser(path)
    if not os.path.exists(p):
        sys.exit(f"missing credential: {path} (see HUBSPOT-INTEGRATION.md)")
    return open(p).read().strip()


def _hs_json(method, url, token, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"HubSpot {method} {url} -> {e.code}: {e.read().decode()[:400]}")


def upload_image(node_id, slug):
    figma = _read_token("~/.figma_token")
    hs = _read_token("~/.hubspot_token")
    # 1) Figma render → temporary url
    u = f"https://api.figma.com/v1/images/{FILE_KEY}?ids={urllib.parse.quote(node_id)}&format=png&scale=2"
    req = urllib.request.Request(u, headers={"X-Figma-Token": figma})
    r = json.loads(urllib.request.urlopen(req, timeout=90).read())
    img_url = (r.get("images") or {}).get(node_id)
    if not img_url:
        sys.exit(f"Figma render failed for node {node_id}: {r}")
    png = urllib.request.urlopen(img_url, timeout=90).read()
    # 2) Upload to File Manager (multipart) as a public, non-indexed file
    boundary = "----bw" + uuid.uuid4().hex

    def field(name, value):
        return (f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n').encode()
    body = field("folderPath", FILES_FOLDER)
    body += field("options", json.dumps({"access": "PUBLIC_NOT_INDEXABLE", "overwrite": True}))
    body += (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; '
             f'filename="{slug}.png"\r\nContent-Type: image/png\r\n\r\n').encode()
    body += png + b"\r\n" + f"--{boundary}--\r\n".encode()
    req = urllib.request.Request("https://api.hubapi.com/files/v3/files", data=body, method="POST",
        headers={"Authorization": f"Bearer {hs}", "Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=120).read())
    except urllib.error.HTTPError as e:
        sys.exit(f"File Manager upload -> {e.code}: {e.read().decode()[:400]}")
    print(res.get("url"))
    return res.get("url")


def _wrap_widget(value):
    """A raw HTML string becomes a rich_text override; a dict passes through verbatim."""
    if isinstance(value, dict):
        return value
    return {"type": "module", "body": {"path": "@hubspot/rich_text", "html": value}}


def create_draft(payload):
    hs = _read_token("~/.hubspot_token")
    widgets = {k: _wrap_widget(v) for k, v in (payload.get("widgets") or {}).items()}
    content = {"templatePath": payload["templatePath"], "widgets": widgets}
    email_id = payload.get("emailId")
    if email_id:
        # update existing draft: merge widgets into current content
        _, cur = _hs_json("GET", f"{V3}/{email_id}", hs)
        merged = cur.get("content", {})
        merged.setdefault("widgets", {}).update(widgets)
        merged["templatePath"] = payload["templatePath"]
        s, d = _hs_json("PATCH", f"{V3}/{email_id}", hs, {
            "name": payload.get("name"), "subject": payload.get("subject"), "content": merged})
    else:
        s, d = _hs_json("POST", CREATE_URL, hs, {
            "name": payload["name"], "subject": payload["subject"], "content": content})
    eid = d.get("id")
    print(json.dumps({
        "id": eid, "state": d.get("state"), "isPublished": d.get("isPublished"),
        "editorUrl": f"https://app.hubspot.com/email/{PORTAL_ID}/edit/{eid}/content"}))
    return d


# ---- slot rendering (one place; keeps override HTML consistent with the template) ----
# Layout mirrors the reference email: logo masthead -> centered hero headline -> optional
# intro -> N stacked feature rows (image, headline, body, button). See design-system.md.

def _hero_headline(t, th):
    return (f"<h1 style='margin:0; font-size:37px; line-height:115%; text-align:center; "
            f"color:{th['ink']}; font-family:{FF};'>{t}</h1>")

def _intro(t, th):
    return (f"<p style='margin:0; font-size:16px; line-height:145%; font-weight:{BODY_WEIGHT}; "
            f"text-align:center; color:{th['body']}; font-family:{FF};'>{t}</p>")

def _button(label, url):
    return (f"<table role='presentation' cellpadding='0' cellspacing='0' border='0'><tr>"
            f"<td align='center' bgcolor='{ACCENT}' style='border-radius:25px;'>"
            f"<a href='{url}' style='display:inline-block; padding:12px 28px; font-family:{FF}; "
            f"font-size:16px; font-weight:bold; color:#FFFFFF; text-decoration:none; border-radius:25px;'>{label}</a>"
            f"</td></tr></table>")

def _feature_row(img_url, headline, body, label, url, alt, th):
    """One stacked feature: full-width image -> headline -> body -> left button. 48px gap below."""
    return (
        f"<table role='presentation' width='100%' cellpadding='0' cellspacing='0' border='0' style='margin:0 0 48px;'>"
        f"<tr><td style='padding:0 0 16px;'>"
        f"<a href='{url}'><img src='{img_url}' width='552' alt='{alt}' "
        f"style='display:block; width:100%; max-width:552px; height:auto; border:0;'></a></td></tr>"
        f"<tr><td style='padding:0 0 8px; font-family:{FF};'>"
        f"<h2 style='margin:0; font-size:30px; line-height:115%; color:{th['ink']}; font-family:{FF};'>{headline}</h2></td></tr>"
        f"<tr><td style='padding:0 0 16px; font-family:{FF};'>"
        f"<p style='margin:0; font-size:16px; line-height:145%; font-weight:{BODY_WEIGHT}; "
        f"color:{th['body']}; font-family:{FF};'>{body}</p></td></tr>"
        f"<tr><td>{_button(label, url)}</td></tr>"
        f"</table>")


def _spec_grid(specs, th):
    """A 2-up grid of small spec items, each with a divider rule above (Apple-style).
    Each spec is {heading, body} -> bold lead + medium continuation. Cells stack on mobile."""
    if not specs:
        return ""
    rows = []
    for i in range(0, len(specs), 2):
        pair = specs[i:i + 2]
        tds = []
        for j, s in enumerate(pair):
            pad = "16px 12px 28px 0" if j == 0 else "16px 0 28px 12px"
            item = (f"<strong style='color:{th['ink']};'>{s.get('heading','')}</strong> "
                    f"<span style='font-weight:{BODY_WEIGHT}; color:{th['body']};'>{s.get('body','')}</span>")
            tds.append(f"<td class='bw-grid-cell' valign='top' width='50%' "
                       f"style='padding:{pad}; border-top:1px solid {th['divider']}; font-family:{FF}; "
                       f"font-size:15px; line-height:145%;'>{item}</td>")
        if len(pair) == 1:  # keep the grid balanced on an odd count
            tds.append("<td class='bw-grid-cell' width='50%' style='padding:0;'>&nbsp;</td>")
        rows.append("<tr>" + "".join(tds) + "</tr>")
    return (f"<table role='presentation' width='100%' cellpadding='0' cellspacing='0' border='0'>"
            f"{''.join(rows)}</table>")


def _resolve_image(feature, lib, slug):
    """A feature image is either a direct URL or an assetKey rendered from Figma + hosted."""
    img = feature["image"]
    if isinstance(img, str) and img.startswith("http"):
        return img
    node = (lib.get("assets", {}).get(img) or {}).get("nodeId")
    if not node:
        sys.exit(f"feature image {img!r} not found in assets/library.json")
    return upload_image(node, f"{slug}-{img}")


def generate(slug):
    reg = json.load(open(os.path.join(ROOT, "renderers/email/newsletters/registry.json")))
    lib = json.load(open(os.path.join(ROOT, "assets/library.json")))
    n = reg.get("newsletters", {}).get(slug)
    if not n:
        sys.exit(f"unknown newsletter slug: {slug!r} (see renderers/email/newsletters/registry.json)")
    features = n.get("features", [])
    if not features:
        sys.exit(f"newsletter {slug!r} has no features")

    variant = n.get("variant", "light")
    th = THEMES.get(variant)
    if not th:
        sys.exit(f"unknown variant {variant!r} (expected one of {list(THEMES)})")
    hub = reg["hubspot"]
    template_path = hub["templatePathDark"] if variant == "dark" else hub["templatePath"]
    if not template_path:
        sys.exit(f"variant {variant!r} has no template path in registry hubspot block")

    rows = []
    for f in features:
        img_url = _resolve_image(f, lib, slug)
        alt = f.get("alt", f.get("headline", ""))
        rows.append(_feature_row(img_url, f["headline"], f["body"],
                                 f.get("ctaLabel", "Learn more"),
                                 f.get("ctaUrl", n.get("ctaUrl", "#")), alt, th))

    widgets = {
        "hero_headline": _hero_headline(n["heroHeadline"], th),
        # always send intro (empty blanks the slot, so the template default never leaks)
        "intro": _intro(n["intro"], th) if n.get("intro") else "",
        "features": "".join(rows),
        # always send specs (empty blanks the slot when a pack has none)
        "specs": _spec_grid(n.get("specs", []), th),
        "preview_text": {"type": "text", "name": "preview_text",
                         "body": {"value": n.get("previewText", "")}},
    }

    return create_draft({
        "name": f"Bluewater Newsletter — {n['displayName']}",
        "subject": n.get("subject", n["displayName"]),
        "templatePath": template_path,
        "widgets": widgets,
    })


def main():
    ap = argparse.ArgumentParser(description="Bluewater newsletter engine (HubSpot drafts).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("upload-image")
    a.add_argument("--node", required=True)
    a.add_argument("--name", required=True)
    b = sub.add_parser("create-draft")
    b.add_argument("--payload", required=True, help="path to JSON payload")
    g = sub.add_parser("generate", help="one-shot: registry slug -> finished HubSpot draft")
    g.add_argument("--slug", required=True)
    args = ap.parse_args()
    if args.cmd == "upload-image":
        upload_image(args.node, args.name)
    elif args.cmd == "create-draft":
        create_draft(json.load(open(args.payload)))
    elif args.cmd == "generate":
        generate(args.slug)


if __name__ == "__main__":
    main()
