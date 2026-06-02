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
FF = "Helvetica,Arial,sans-serif"
NAVY = "#00205B"   # blue/950 — eyebrow accent + CTA
INK = "#18181B"    # gray/900 — headline + spec heading
BODY = "#52525B"   # gray/600 — intro
MUTED = "#71717A"  # gray/500 — spec body


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

def _hero(url):
    return (f"<img src='{url}' width='600' alt='' style='display:block; width:100%; "
            f"max-width:600px; height:auto; border:0;'>")

def _eyebrow(t):
    return f"<p style='margin:0 0 8px; font-size:14px; font-weight:bold; color:{NAVY}; font-family:{FF};'>{t}</p>"

def _headline(t):
    return f"<h1 style='margin:0; font-size:30px; line-height:36px; color:{INK}; font-family:{FF};'>{t}</h1>"

def _intro(t):
    return f"<p style='margin:0; font-size:16px; line-height:24px; color:{BODY}; font-family:{FF};'>{t}</p>"

def _spec(s):
    h, b = s.get("heading", ""), s.get("body", "")
    return (f"<p style='margin:0 0 4px; font-size:16px; font-weight:bold; color:{INK}; font-family:{FF};'>{h}</p>"
            f"<p style='margin:0; font-size:14px; line-height:20px; color:{MUTED}; font-family:{FF};'>{b}</p>")

def _cta(label, url):
    return (f"<table role='presentation' cellpadding='0' cellspacing='0' border='0'><tr>"
            f"<td align='center' bgcolor='{NAVY}' style='border-radius:6px;'>"
            f"<a href='{url}' style='display:inline-block; padding:14px 28px; font-family:{FF}; "
            f"font-size:16px; font-weight:bold; color:#FFFFFF; text-decoration:none; border-radius:6px;'>{label}</a>"
            f"</td></tr></table>")


def generate(slug):
    reg = json.load(open(os.path.join(ROOT, "renderers/email/newsletters/registry.json")))
    lib = json.load(open(os.path.join(ROOT, "assets/library.json")))
    n = reg.get("newsletters", {}).get(slug)
    if not n:
        sys.exit(f"unknown newsletter slug: {slug!r} (see renderers/email/newsletters/registry.json)")
    node = (lib.get("assets", {}).get(n["heroAsset"]) or {}).get("nodeId")
    if not node:
        sys.exit(f"heroAsset {n['heroAsset']!r} not found in assets/library.json")
    hero_url = upload_image(node, n["heroAsset"])
    s = n["slots"]
    cta_url = n.get("ctaUrl", "#")
    widgets = {
        "hero_image": _hero(hero_url),
        "eyebrow": _eyebrow(s["eyebrow"]),
        "headline": _headline(s["headline"]),
        "intro": _intro(s["intro"]),
        "spec_1": _spec(s["spec_1"]),
        "spec_2": _spec(s["spec_2"]),
        "spec_3": _spec(s["spec_3"]),
        "cta": _cta(s["cta"], cta_url),
        "preview_text": {"type": "text", "name": "preview_text",
                         "body": {"value": n.get("previewText", "")}},
    }
    return create_draft({
        "name": f"Bluewater Newsletter — {n['displayName']}",
        "subject": n.get("subject", n["displayName"]),
        "templatePath": reg["hubspot"]["templatePath"],
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
