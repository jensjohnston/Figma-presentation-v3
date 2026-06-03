# Newsletter Renderer (HubSpot) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a second renderer to this repo that turns a product's verified content into a live, sendable **draft** HubSpot marketing email, reusing the existing product/asset libraries.

**Architecture:** One repo, "shared core + multiple renderers." Add `core/` (brand tokens) and `renderers/email/` *alongside* the unchanged Figma pipeline. A newsletter = pick a product → fill a rigid HubSpot email template's named slots with that product's verified copy/specs/images → create a draft marketing email via HubSpot's API. Canonical template lives in HubSpot; the repo holds a mirror registry (same pattern as product packs).

**Tech Stack:** Markdown slash commands (Claude-as-engine), JSON registries, Python 3 stdlib validators (pytest for TDD), HubSpot Developer MCP (`mcp__HubSpotDev__*`) + `hs` CLI for the email API.

**Spec:** `docs/superpowers/specs/2026-06-02-bluewater-designer-newsletters-design.md`

---

## Codebase reality (read before starting)

- **No build step, no runtime.** "Claude is the engine." The only executable, unit-testable code is the Python validators in `tools/`. Registries are data; slash commands and the design system are Markdown prompts Claude follows.
- **TDD applies to `tools/validate_newsletters.py` only** (Task 7). For data/Markdown/HubSpot tasks, "verification" means: JSON parses, the validator prints `OK`, or a draft email actually appears in HubSpot and renders correctly. Do not fabricate unit tests for Markdown files.
- **Mirror existing patterns exactly:** `tools/validate_products.py`, `products/registry.json`, `.claude/commands/index-product.md`.
- **Standing rule:** commit locally, **never `git push`** unless told.
- **Branch:** all work on `feature/newsletter-designer` (already checked out).

## File structure (created / modified)

| Path | Responsibility |
|---|---|
| `core/brand-tokens.json` | NEW. Machine-readable Bluewater colors + per-medium font stacks. Canonical color source for the email renderer. |
| `renderers/email/HUBSPOT-INTEGRATION.md` | NEW. Spike output: the exact, verified HubSpot API/MCP calls to create a coded email template and a draft marketing email. Read by Tasks 8–10. |
| `renderers/email/email-design-system.md` | NEW. Email rendering rules (Helvetica stack, 600px tables, inline styles, type scale, CAN-SPAM). Evolves as we test. |
| `renderers/email/newsletters/registry.json` | NEW. Mirror of the rigid HubSpot template's named slots, per product. |
| `tools/validate_newsletters.py` | NEW. Regression gate for the newsletter registry. Pure stdlib. |
| `tools/test_validate_newsletters.py` | NEW. pytest tests for the validator. |
| `.claude/commands/generate-newsletter.md` | NEW. The fill-slots-and-push-draft command. |
| `.claude/commands/index-newsletter.md` | NEW. Mirrors a HubSpot template into the registry (like `/index-product`). |
| `CLAUDE.md` | MODIFY. Document the email renderer + new commands. |

## Execution phases

- **Phase A (Tasks 1–2):** Shared core. Safe, additive, no HubSpot. Execution-ready.
- **Phase B (Task 3):** HubSpot spike. Resolves the API unknown. **Replanning checkpoint after this task** — confirm Tasks 4–10 against `HUBSPOT-INTEGRATION.md` before continuing.
- **Phase C (Tasks 4–10):** Email renderer. Written to current certainty; HubSpot-API specifics reference the spike's notes file.

---

## Phase A — Shared core

### Task 1: Extract brand tokens to `core/brand-tokens.json`

**Files:**
- Create: `core/brand-tokens.json`
- Read for source values: `templates/design-system.md` (colors section)

- [ ] **Step 1: Read the canonical colors**

Run: `grep -n -iE "gray|blue|rose|green|#[0-9a-fA-F]{6}|token" templates/design-system.md | head -60`
Expected: the Gray/Blue/Rose/Green token scales with hex values.

- [ ] **Step 2: Write `core/brand-tokens.json`**

Use the actual hex values found in Step 1. Structure (fill `colors` from the design system — example shape, not invented values):

```json
{
  "_doc": "Medium-agnostic Bluewater brand tokens. Canonical color source for the email renderer; the Figma renderer still reads colors from templates/design-system.md (repoint later if desired). Font stacks differ per medium because email cannot use custom web fonts.",
  "colors": {
    "gray": { "500": "<hex from design-system.md>", "...": "..." },
    "blue": { "...": "..." },
    "rose": { "...": "..." },
    "green": { "...": "..." }
  },
  "fontStacks": {
    "figma": "Suisse Int'l",
    "email": "Helvetica, Arial, sans-serif"
  },
  "typescaleRatio": 1.2
}
```

- [ ] **Step 3: Verify it parses and colors match the source**

Run: `python3 -c "import json; d=json.load(open('core/brand-tokens.json')); print(sorted(d['colors']), d['fontStacks']['email'])"`
Expected: prints the color scale names and `Helvetica, Arial, sans-serif`. Spot-check 2–3 hex values against `templates/design-system.md`.

- [ ] **Step 4: Commit**

```bash
git add core/brand-tokens.json
git commit -m "feat(core): add brand-tokens.json (colors + per-medium font stacks)"
```

### Task 2: Scaffold the email renderer directory

**Files:**
- Create: `renderers/email/newsletters/.gitkeep`

- [ ] **Step 1: Create the directory structure**

Run: `mkdir -p renderers/email/newsletters && touch renderers/email/newsletters/.gitkeep`

- [ ] **Step 2: Verify**

Run: `ls -R renderers/`
Expected: `renderers/email/newsletters/.gitkeep` exists.

- [ ] **Step 3: Commit**

```bash
git add renderers/email/newsletters/.gitkeep
git commit -m "chore(email): scaffold renderers/email directory"
```

---

## Phase B — HubSpot spike (resolves the API unknown)

### Task 3: Confirm HubSpot email API + push a "hello world" draft

This task is exploratory by nature but has concrete deliverables. Its purpose is to replace assumptions with verified facts before any command is written.

**Files:**
- Create: `renderers/email/HUBSPOT-INTEGRATION.md`

- [ ] **Step 1: Authenticate the HubSpot CLI / MCP**

The HubSpot dev MCP currently errors `No account ID found`. Resolve auth first. Suggest the user run, in this session:
`! hs account auth`
(interactive login — must be run by the user). Then confirm with `! hs account list`.
Expected: the Bluewater portal is listed as the default account.

- [ ] **Step 2: Pull the authoritative docs**

Use `mcp__HubSpotDev__search-docs` then `mcp__HubSpotDev__fetch-doc` for:
(a) creating a **coded email template** (HTML+HubL) in the Design Manager, and
(b) creating a **draft marketing email** from a template via API (the marketing emails endpoint).
Record the exact endpoints/MCP tools and required scopes.

- [ ] **Step 3: Push a minimal "hello world" draft**

Create the smallest possible coded email template (one heading, Helvetica stack, 600px table) and create ONE **draft** marketing email from it. Do not send.

- [ ] **Step 4: Verify in HubSpot**

Confirm the draft exists in the HubSpot Marketing → Email UI and the heading renders. Capture the template ID and email ID.

- [ ] **Step 5: Write `renderers/email/HUBSPOT-INTEGRATION.md`**

Document, with no ambiguity: the exact MCP tools / API endpoints used, auth/scopes required, how a template's editable regions map to "slots," how to set slot values when creating the email, the IDs of the hello-world artifacts, and any gotchas (e.g. modules vs raw HubL, image hosting requirement).

- [ ] **Step 6: Commit**

```bash
git add renderers/email/HUBSPOT-INTEGRATION.md
git commit -m "docs(email): verified HubSpot email-creation integration notes (spike)"
```

> **REPLANNING CHECKPOINT.** Before Task 4, re-read this plan's Phase C against `HUBSPOT-INTEGRATION.md`. If the spike revealed the slot mechanism, image hosting, or API shape differs from assumptions here, update Tasks 4–10 accordingly. Get user sign-off on any material change.

---

## Phase C — Email renderer

### Task 4: Write the first `email-design-system.md`

**Files:**
- Create: `renderers/email/email-design-system.md`

- [ ] **Step 1: Write the rules doc**

Capture the spec §5 constraints as actionable rules: Helvetica stack (`Helvetica, Arial, sans-serif`), single-column ≤600px, table-based layout, inline styles only, email type scale (H1 28–32px, body 14–16px, line-heights px/unitless), hosted-URL images with alt text + no critical copy in images, bulletproof table buttons, mandatory CAN-SPAM footer, dark-mode caution. Reference `core/brand-tokens.json` for colors. State explicitly that this doc evolves as cross-client rendering is tested.

- [ ] **Step 2: Verify it covers every §5 constraint**

Run: `grep -ic -E "helvetica|600|table|inline|alt|footer|unsubscribe" renderers/email/email-design-system.md`
Expected: a non-zero count for each term (spot-check the doc reads coherently).

- [ ] **Step 3: Commit**

```bash
git add renderers/email/email-design-system.md
git commit -m "docs(email): first email design system (constraints locked in)"
```

### Task 5: Define the newsletter registry schema + first entry

**Files:**
- Create: `renderers/email/newsletters/registry.json`
- Reference: `products/registry.json` (slot pattern), `HUBSPOT-INTEGRATION.md` (slot mechanism)

- [ ] **Step 1: Write `registry.json` mirroring the product-pack shape**

Use the slot mechanism confirmed in Task 3. Shape:

```json
{
  "_doc": "Newsletter template mirror. Source of truth = the rigid HubSpot email template; this file is a generated index (rebuild via /index-newsletter). Slots show the current editable text the generator rewrites. Validated by tools/validate_newsletters.py.",
  "hubspot": { "templateId": "<from Task 3>", "portal": "<account>" },
  "slotVocabulary": ["headline", "subhead", "body", "key-specs", "product-image", "cta-label", "cta-url"],
  "newsletters": {
    "product-spotlight": {
      "displayName": "Product Spotlight",
      "templateId": "<HubSpot coded template id>",
      "slots": {
        "headline": "", "subhead": "", "body": "",
        "key-specs": "", "product-image": "", "cta-label": "", "cta-url": ""
      }
    }
  }
}
```

- [ ] **Step 2: Verify it parses**

Run: `python3 -c "import json; d=json.load(open('renderers/email/newsletters/registry.json')); print(list(d['newsletters']), d['slotVocabulary'])"`
Expected: prints `['product-spotlight']` and the slot vocabulary.

- [ ] **Step 3: Commit**

```bash
git add renderers/email/newsletters/registry.json
git commit -m "feat(email): newsletter registry schema + first template mirror"
```

### Task 6: Add a hosted-URL field to the asset library (for email images)

**Files:**
- Modify: `assets/library.json`

- [ ] **Step 1: Inspect current asset shape**

Run: `python3 -c "import json; d=json.load(open('assets/library.json')); k=next(iter(d['assets'])); print(k, d['assets'][k])"`
Expected: one asset showing its current fields (e.g. `nodeId`, `tags`, `description`).

- [ ] **Step 2: Add an optional `emailUrl` field to assets used by the first newsletter**

For each asset the `product-spotlight` newsletter will reference, add `"emailUrl": "<public https URL>"` alongside the existing `nodeId` (host per the decision recorded in Task 3 — HubSpot file manager vs existing CDN). Leave other assets untouched (field is optional/additive).

- [ ] **Step 3: Verify it parses and Figma nodeIds are intact**

Run: `python3 -c "import json; d=json.load(open('assets/library.json')); a=[v for v in d['assets'].values() if 'emailUrl' in v]; print(len(a), 'have emailUrl;', all('nodeId' in v for v in d['assets'].values()), 'all keep nodeId')"`
Expected: a non-zero count with `emailUrl`, and `True` that every asset still has `nodeId`.

- [ ] **Step 4: Commit**

```bash
git add assets/library.json
git commit -m "feat(assets): add optional emailUrl for email-renderer image hosting"
```

### Task 7: TDD the newsletter validator

**Files:**
- Create: `tools/validate_newsletters.py`
- Test: `tools/test_validate_newsletters.py`

- [ ] **Step 1: Write the failing test**

```python
# tools/test_validate_newsletters.py
import json, subprocess, sys, pathlib, textwrap

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "validate_newsletters.py"


def run():
    return subprocess.run([sys.executable, str(SCRIPT)],
                          capture_output=True, text=True)


def test_real_registry_passes():
    r = run()
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.startswith("OK"), r.stdout


def test_unknown_slot_fails(tmp_path, monkeypatch):
    # A newsletter using a slot outside slotVocabulary must FAIL.
    reg = json.load(open(ROOT / "renderers/email/newsletters/registry.json"))
    reg["newsletters"]["bad"] = {
        "displayName": "Bad", "templateId": "x",
        "slots": {"not-a-real-slot": ""}
    }
    bad = tmp_path / "registry.json"
    bad.write_text(json.dumps(reg))
    monkeypatch.setenv("NEWSLETTER_REGISTRY", str(bad))
    r = run()
    assert r.returncode == 1
    assert "not-a-real-slot" in r.stdout
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/jens.johnston/Documents/Figma-presentation-v3 && tools/.venv/bin/python -m pytest tools/test_validate_newsletters.py -v`
Expected: FAIL — `validate_newsletters.py` does not exist yet.

- [ ] **Step 3: Write the validator (mirrors `validate_products.py`)**

```python
#!/usr/bin/env python3
"""Validate renderers/email/newsletters/registry.json against the newsletter contract.

Regression gate for the newsletter library. Checks every newsletter has the
required fields and every slot key is in slotVocabulary. Honors the
NEWSLETTER_REGISTRY env var (used by tests) and falls back to the repo file.
"""
import json, os, sys, pathlib


def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    reg_path = os.environ.get(
        "NEWSLETTER_REGISTRY",
        root / "renderers" / "email" / "newsletters" / "registry.json")
    reg = json.load(open(reg_path))
    vocab = set(reg.get("slotVocabulary", []))
    errors = []
    newsletters = reg.get("newsletters", {})
    if not newsletters:
        errors.append("no newsletters defined")
    if not vocab:
        errors.append("slotVocabulary is empty")
    for slug, n in newsletters.items():
        for field in ("displayName", "templateId", "slots"):
            if field not in n:
                errors.append(f"{slug}: missing '{field}'")
        for key in n.get("slots", {}):
            if key not in vocab:
                errors.append(f"{slug}: slot {key!r} not in slotVocabulary")
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print(f"OK — {len(newsletters)} newsletters")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd /Users/jens.johnston/Documents/Figma-presentation-v3 && tools/.venv/bin/python -m pytest tools/test_validate_newsletters.py -v`
Expected: PASS (both tests).

- [ ] **Step 5: Commit**

```bash
git add tools/validate_newsletters.py tools/test_validate_newsletters.py
git commit -m "feat(tools): validate_newsletters.py + tests (regression gate)"
```

### Task 8: Write the `/index-newsletter` command

**Files:**
- Create: `.claude/commands/index-newsletter.md`
- Reference: `.claude/commands/index-product.md`, `renderers/email/HUBSPOT-INTEGRATION.md`

- [ ] **Step 1: Write the command**

Mirror `index-product.md`'s structure. It must: read a HubSpot coded email template (via the MCP confirmed in Task 3), extract its editable regions as named slots, propose the `displayName`/`slotVocabulary` mapping (user confirms), write/update the entry in `renderers/email/newsletters/registry.json`, then run `tools/.venv/bin/python tools/validate_newsletters.py` and require `OK`.

- [ ] **Step 2: Verify the command references the validator gate**

Run: `grep -c "validate_newsletters.py" .claude/commands/index-newsletter.md`
Expected: ≥1.

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/index-newsletter.md
git commit -m "feat(command): /index-newsletter (mirror HubSpot template into registry)"
```

### Task 9: Write the `/generate-newsletter` command

**Files:**
- Create: `.claude/commands/generate-newsletter.md`
- Reference: `generate-presentation.md` (orchestration style), `HUBSPOT-INTEGRATION.md`, `email-design-system.md`

- [ ] **Step 1: Write the command**

It must orchestrate: (1) take a `<product-slug>` arg; (2) load that product's verified `content` + `images` from `products/registry.json` + `assets/library.json` (using `emailUrl` for images); (3) load the target newsletter template's slots from `renderers/email/newsletters/registry.json`; (4) fill slots within the rigid system per `email-design-system.md` (Helvetica, 600px, etc.); (5) create a **DRAFT** marketing email in HubSpot via the API documented in `HUBSPOT-INTEGRATION.md` — **never auto-send**; (6) report the draft URL/ID back to the user for review.

- [ ] **Step 2: Verify the no-auto-send guard and product-library reuse are explicit**

Run: `grep -ciE "draft|never send|do not send" .claude/commands/generate-newsletter.md && grep -c "products/registry.json" .claude/commands/generate-newsletter.md`
Expected: both ≥1.

- [ ] **Step 3: End-to-end manual verification**

Run `/generate-newsletter kitchen-station`. Confirm a draft appears in HubSpot, uses the product's real specs/copy, images load via `emailUrl`, Helvetica renders, and nothing was sent.

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/generate-newsletter.md
git commit -m "feat(command): /generate-newsletter (product -> HubSpot draft email)"
```

### Task 10: Document the renderer in `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add an "Email Renderer (Newsletters)" section**

Document: the `core/` + `renderers/email/` layout, the `/generate-newsletter` and `/index-newsletter` commands, the draft-only rule, the Helvetica/email-constraints pointer, and `tools/validate_newsletters.py` as the gate. Mirror the brevity of the existing "Product Content Library" section.

- [ ] **Step 2: Verify**

Run: `grep -c "generate-newsletter" CLAUDE.md`
Expected: ≥1.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: document the email/newsletter renderer in CLAUDE.md"
```

---

## Self-review (completed by author)

- **Spec coverage:** §2 one-repo (architecture intro) ✓; §3 core/ + renderers/email (Tasks 1–2, 4–5) ✓; §4 workflow (Task 9) ✓; §5 email constraints (Task 4) ✓; §6 build order — Step 0 reorg (Tasks 1–2), Step 1 spike (Task 3), Step 2 rigidify (Tasks 4–5, 8), Step 3 generate (Task 9), Step 4 validator (Task 7) ✓; §7 image hosting (Task 6), API surface (Task 3) ✓.
- **Divergence from spec §3 (intentional, lower-risk):** `templates/` is NOT physically relocated under `renderers/figma/`; the Figma pipeline stays in place to avoid rewriting `generate-presentation.md`. Architecture (shared core, separate renderers) is preserved. `voice.md` dropped from MVP (YAGNI — only needed for out-of-scope topic-to-draft).
- **Placeholder scan:** `<...>` markers are real values intentionally resolved during a task (hex colors from the design system; HubSpot IDs from the Task 3 spike) — each has an explicit source, not a TODO.
- **Type consistency:** `slotVocabulary`/`slots`/`templateId` used identically across Tasks 5, 7, 8, 9. Validator honors `NEWSLETTER_REGISTRY` in both code and test. Validator invoked as `tools/.venv/bin/python` consistently.
