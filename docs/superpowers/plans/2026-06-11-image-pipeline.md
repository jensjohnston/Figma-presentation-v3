# Image Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the SharePoint import + vision-indexed asset library + curated generation flow specified in `docs/superpowers/specs/2026-06-11-image-pipeline-design.md`.

**Architecture:** This project has no build step — Claude is the engine. "Implementation" means: Python validators (the only conventionally-testable code, TDD applies), JSON registries (schema work), and markdown command files in `.claude/commands/` (the executable instructions Claude follows at runtime). Verification for non-Python work = validator gates + live dry runs against the Figma file.

**Tech Stack:** Python 3 (stdlib only, pytest for tests), Figma MCP (`use_figma`, `get_screenshot`, `upload_assets`), MS365 MCP (`sharepoint_search`, `sharepoint_folder_search`, `read_resource`).

**Execution notes:**
- Tasks 2, 4, 9, 10 need live MCP access (Figma; Task 4 also MS365). If executing via subagents, those agents must load MCP tools via ToolSearch; if MCP auth is unavailable in a subagent, run those tasks inline in the main session.
- The Figma file is `GkUiwJTK5Xi65AKw4MOjTL` (Bluewater 2026). Brand Assets page: `51124:14`.
- All `python3`/`pytest` commands run from the repo root.

---

### Task 1: Asset library v2 validator (`tools/validate_assets.py`)

Mirrors `tools/validate_products.py` (script shape, `OK —`/`FAIL` output, exit codes) and `tools/test_validate_newsletters.py` (subprocess tests with env-var registry override).

**Files:**
- Create: `tools/validate_assets.py`
- Create: `tools/test_validate_assets.py`

- [ ] **Step 1: Write the failing tests** (fixtures only — the real library isn't v2 yet; the real-library test is added in Task 2 after backfill)

```python
#!/usr/bin/env python3
"""Tests for tools/validate_assets.py — fixture-driven via ASSETS_LIBRARY env var."""
import json, os, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "validate_assets.py"


def run(env=None):
    return subprocess.run([sys.executable, str(SCRIPT)],
                          capture_output=True, text=True, env=env)


def _env(tmp_path, library, prefs=None):
    lib = tmp_path / "library.json"
    lib.write_text(json.dumps(library))
    e = dict(os.environ)
    e["ASSETS_LIBRARY"] = str(lib)
    p = tmp_path / "preferences.json"
    if prefs is not None:
        p.write_text(json.dumps(prefs))
    e["ASSETS_PREFERENCES"] = str(p)  # points at a missing file when prefs is None
    return e


def _good_asset():
    return {
        "nodeId": "1:1",
        "tags": ["product", "purifier"],
        "description": "Spirit purifier front view on white",
        "source": {"type": "figma"},
        "visual": {
            "aspect": 1.5, "orientation": "landscape", "tone": "light",
            "subject": "center", "suitability": ["card", "hero"], "quality": "high",
        },
    }


def _base():
    return {"assetPageId": "51124:14", "assetPageName": "Brand Assets",
            "assets": {"spirit-front": _good_asset()}}


def test_good_library_passes(tmp_path):
    r = run(_env(tmp_path, _base()))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.startswith("OK"), r.stdout


def test_missing_visual_fails(tmp_path):
    lib = _base()
    del lib["assets"]["spirit-front"]["visual"]
    r = run(_env(tmp_path, lib))
    assert r.returncode == 1
    assert "visual" in r.stdout


def test_missing_source_fails(tmp_path):
    lib = _base()
    del lib["assets"]["spirit-front"]["source"]
    r = run(_env(tmp_path, lib))
    assert r.returncode == 1
    assert "source" in r.stdout


def test_bad_tone_fails(tmp_path):
    lib = _base()
    lib["assets"]["spirit-front"]["visual"]["tone"] = "bright"
    r = run(_env(tmp_path, lib))
    assert r.returncode == 1
    assert "tone" in r.stdout


def test_orientation_aspect_mismatch_fails(tmp_path):
    lib = _base()
    lib["assets"]["spirit-front"]["visual"]["orientation"] = "portrait"  # aspect 1.5
    r = run(_env(tmp_path, lib))
    assert r.returncode == 1
    assert "orientation" in r.stdout


def test_empty_suitability_fails(tmp_path):
    lib = _base()
    lib["assets"]["spirit-front"]["visual"]["suitability"] = []
    r = run(_env(tmp_path, lib))
    assert r.returncode == 1
    assert "suitability" in r.stdout


def test_duplicate_nodeid_fails(tmp_path):
    lib = _base()
    lib["assets"]["spirit-side"] = _good_asset()  # same nodeId "1:1"
    r = run(_env(tmp_path, lib))
    assert r.returncode == 1
    assert "duplicate nodeId" in r.stdout


def test_unknown_source_type_fails(tmp_path):
    lib = _base()
    lib["assets"]["spirit-front"]["source"]["type"] = "dropbox"
    r = run(_env(tmp_path, lib))
    assert r.returncode == 1
    assert "source.type" in r.stdout
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tools/test_validate_assets.py -v`
Expected: all FAIL/ERROR (script does not exist yet).

- [ ] **Step 3: Write the validator**

```python
#!/usr/bin/env python3
"""Validate assets/library.json (v2 schema) against the asset contract.

Regression gate for the asset library. Every asset must carry the
vision-index metadata (visual block) and provenance (source block) the
generator's image matching depends on. Also validates
assets/preferences.json when it exists (see Task 3).

Honors ASSETS_LIBRARY / ASSETS_PREFERENCES env vars (used by tests);
otherwise reads the repo files.
"""
import json, os, sys, pathlib

TONES = {"light", "dark", "mixed"}
SUBJECTS = {"center", "left", "right", "top", "bottom"}
SUITABILITY = {"hero", "full-bleed", "card", "detail", "texture"}
QUALITY = {"high", "medium", "low"}
ORIENTATIONS = {"landscape", "portrait", "square"}
SOURCE_TYPES = {"figma", "sharepoint", "onedrive-sync"}


def orientation_for(aspect):
    if 0.9 <= aspect <= 1.1:
        return "square"
    return "landscape" if aspect > 1.1 else "portrait"


def check_assets(lib):
    errors = []
    assets = lib.get("assets", {})
    if not assets:
        errors.append("no assets defined")
    seen_nodes = {}
    for key, a in assets.items():
        for field in ("nodeId", "tags", "description", "source", "visual"):
            if field not in a:
                errors.append(f"{key}: missing '{field}'")
        node = a.get("nodeId")
        if node in seen_nodes:
            errors.append(f"{key}: duplicate nodeId {node} (also {seen_nodes[node]})")
        seen_nodes[node] = key
        if not isinstance(a.get("tags"), list) or not a.get("tags"):
            errors.append(f"{key}: tags must be a non-empty list")
        src = a.get("source", {})
        if src.get("type") not in SOURCE_TYPES:
            errors.append(f"{key}: bad source.type {src.get('type')!r}")
        v = a.get("visual", {})
        if not v:
            continue
        aspect = v.get("aspect")
        if not isinstance(aspect, (int, float)) or aspect <= 0:
            errors.append(f"{key}: visual.aspect must be a positive number")
        elif v.get("orientation") != orientation_for(aspect):
            errors.append(f"{key}: orientation {v.get('orientation')!r} "
                          f"inconsistent with aspect {aspect}")
        if v.get("orientation") not in ORIENTATIONS:
            errors.append(f"{key}: bad orientation {v.get('orientation')!r}")
        if v.get("tone") not in TONES:
            errors.append(f"{key}: bad tone {v.get('tone')!r}")
        if v.get("subject") not in SUBJECTS:
            errors.append(f"{key}: bad subject {v.get('subject')!r}")
        suit = v.get("suitability")
        if not isinstance(suit, list) or not suit or not set(suit) <= SUITABILITY:
            errors.append(f"{key}: bad suitability {suit!r}")
        if v.get("quality") not in QUALITY:
            errors.append(f"{key}: bad quality {v.get('quality')!r}")
    return errors


def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    lib_path = os.environ.get("ASSETS_LIBRARY", str(root / "assets" / "library.json"))
    lib = json.load(open(lib_path))
    errors = check_assets(lib)
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print(f"OK — {len(lib.get('assets', {}))} assets")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tools/test_validate_assets.py -v`
Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/validate_assets.py tools/test_validate_assets.py
git commit -m "feat(assets): v2 library validator (visual + source blocks)"
```

---

### Task 2: Backfill the 13 existing assets to schema v2

Live Figma work — needs the Figma MCP. Each asset gets `source` + `visual` written from an actual look at the image.

**Files:**
- Modify: `assets/library.json`
- Modify: `tools/test_validate_assets.py` (add the real-library test)

- [ ] **Step 1: Load the figma-use skill, then measure all 13 nodes in one `use_figma` call**

Invoke the `figma:figma-use` skill first (mandatory before `use_figma`). Then run (fileKey `GkUiwJTK5Xi65AKw4MOjTL`):

```javascript
// Measure every library asset node: dimensions -> aspect/orientation
const ids = ["51121:6380","61219:17726","61219:17869","61219:17972","61219:17844",
             "61219:17849","61219:17796","61219:17998","61219:18017","61219:18000",
             "61219:17840","61219:18012","61219:17966"];
const out = [];
for (const id of ids) {
  const n = await figma.getNodeByIdAsync(id);
  out.push(n ? { id, name: n.name, w: Math.round(n.width), h: Math.round(n.height) }
             : { id, missing: true });
}
return out;
```

If any node reports `missing: true`, STOP and report — the library is stale and must be fixed (correct nodeId or remove the entry) before backfilling.

- [ ] **Step 2: Screenshot each asset node**

Call `get_screenshot` for each of the 13 nodeIds (fileKey `GkUiwJTK5Xi65AKw4MOjTL`). Look at each image and decide:
- `tone`: is the image predominantly light, dark, or mixed?
- `subject`: where does the visual subject sit (center/left/right/top/bottom)?
- `suitability`: lifestyle/atmospheric shots wide enough for a 1.78 slide → include `full-bleed`+`hero`; packshots on plain background → `card`+`detail`; macro/abstract (e.g. `superiorosmosis-membrane-zoom`) → `detail`+`texture`; app screens → `card`.
- `quality`: `high` unless the screenshot shows visible blur/banding/compression at 2x → `medium`, unusable-soft → `low`.

- [ ] **Step 3: Write the v2 entries**

For every asset in `assets/library.json`, keep `nodeId`/`tags`/`description` (expand thin descriptions to a full visual sentence — what the image actually shows, setting, lighting) and add:

```json
"source": { "type": "figma" },
"visual": {
  "aspect": <w/h from Step 1, 2 decimals>,
  "orientation": "<landscape|portrait|square — square when 0.9 ≤ aspect ≤ 1.1>",
  "tone": "<from Step 2>",
  "subject": "<from Step 2>",
  "suitability": [<from Step 2>],
  "quality": "<from Step 2>"
}
```

Keep the existing top-level `assetPageId`, `assetPageName`, `note` keys unchanged.

- [ ] **Step 4: Run the validator on the real library**

Run: `python3 tools/validate_assets.py`
Expected: `OK — 13 assets`

- [ ] **Step 5: Add the real-library regression test**

Append to `tools/test_validate_assets.py`:

```python
def test_real_library_passes():
    r = run()
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.startswith("OK"), r.stdout
```

Run: `python3 -m pytest tools/test_validate_assets.py -v`
Expected: 9 passed.

- [ ] **Step 6: Commit**

```bash
git add assets/library.json tools/test_validate_assets.py
git commit -m "feat(assets): backfill library to v2 — vision metadata for all 13 assets"
```

---

### Task 3: Preference memory scaffold + validator coverage

**Files:**
- Create: `assets/preferences.json`
- Modify: `tools/validate_assets.py`
- Modify: `tools/test_validate_assets.py`

- [ ] **Step 1: Write the failing tests**

Append to `tools/test_validate_assets.py`:

```python
def _good_prefs():
    return {
        "imagePicks": [
            {"context": {"role": "hero", "topic": "spirit purifier", "slot": "full-bleed"},
             "chosen": "spirit-front", "rejected": [], "date": "2026-06-11"}
        ],
        "templatePicks": [
            {"context": {"contentShape": "4 items, image-rich", "deck": "demo"},
             "chosen": "template-bento4", "rejected": ["pillar-grid-4up-image"],
             "date": "2026-06-11"}
        ],
    }


def test_good_preferences_pass(tmp_path):
    r = run(_env(tmp_path, _base(), prefs=_good_prefs()))
    assert r.returncode == 0, r.stdout + r.stderr


def test_missing_preferences_file_passes(tmp_path):
    r = run(_env(tmp_path, _base()))  # prefs=None -> env points at missing file
    assert r.returncode == 0, r.stdout + r.stderr


def test_unknown_image_pick_fails(tmp_path):
    prefs = _good_prefs()
    prefs["imagePicks"][0]["chosen"] = "no-such-asset"
    r = run(_env(tmp_path, _base(), prefs=prefs))
    assert r.returncode == 1
    assert "no-such-asset" in r.stdout


def test_unknown_template_pick_fails(tmp_path):
    prefs = _good_prefs()
    prefs["templatePicks"][0]["chosen"] = "template-does-not-exist"
    r = run(_env(tmp_path, _base(), prefs=prefs))
    assert r.returncode == 1
    assert "template-does-not-exist" in r.stdout


def test_custom_template_pick_passes(tmp_path):
    prefs = _good_prefs()
    prefs["templatePicks"][0]["chosen"] = "custom"  # escape-hatch builds log as "custom"
    r = run(_env(tmp_path, _base(), prefs=prefs))
    assert r.returncode == 0, r.stdout + r.stderr
```

- [ ] **Step 2: Run tests to verify the new ones fail**

Run: `python3 -m pytest tools/test_validate_assets.py -v`
Expected: the 5 new tests FAIL (validator ignores preferences); earlier 9 still pass.

- [ ] **Step 3: Extend the validator**

In `tools/validate_assets.py`, add after `check_assets`:

```python
def check_preferences(prefs, asset_keys, template_names):
    errors = []
    for i, p in enumerate(prefs.get("imagePicks", [])):
        for k in [p.get("chosen"), *p.get("rejected", [])]:
            if k not in asset_keys:
                errors.append(f"imagePicks[{i}]: unknown assetKey {k!r}")
        if "context" not in p or "date" not in p:
            errors.append(f"imagePicks[{i}]: missing context/date")
    for i, p in enumerate(prefs.get("templatePicks", [])):
        for k in [p.get("chosen"), *p.get("rejected", [])]:
            # "custom" = escape-hatch build; "product:<slug>/<role>" = product-pack slide
            if k not in template_names and k != "custom" and not str(k).startswith("product:"):
                errors.append(f"templatePicks[{i}]: unknown template {k!r}")
        if "context" not in p or "date" not in p:
            errors.append(f"templatePicks[{i}]: missing context/date")
    return errors
```

And replace the body of `main()` with:

```python
def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    lib_path = os.environ.get("ASSETS_LIBRARY", str(root / "assets" / "library.json"))
    lib = json.load(open(lib_path))
    errors = check_assets(lib)

    prefs_path = pathlib.Path(os.environ.get(
        "ASSETS_PREFERENCES", str(root / "assets" / "preferences.json")))
    n_picks = 0
    if prefs_path.exists():
        prefs = json.load(open(prefs_path))
        reg = json.load(open(root / "templates" / "registry.json"))
        errors += check_preferences(prefs, set(lib.get("assets", {})),
                                    set(reg.get("templates", {})))
        n_picks = len(prefs.get("imagePicks", [])) + len(prefs.get("templatePicks", []))

    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print(f"OK — {len(lib.get('assets', {}))} assets, {n_picks} preference records")
```

Note: `check_preferences` validates template names against the real `templates/registry.json` even under test fixtures — `template-bento4` and `pillar-grid-4up-image` exist there, which is why the fixture uses those names.

- [ ] **Step 4: Run all tests**

Run: `python3 -m pytest tools/test_validate_assets.py -v`
Expected: 14 passed.

- [ ] **Step 5: Create the empty preferences file**

Create `assets/preferences.json`:

```json
{
  "imagePicks": [],
  "templatePicks": []
}
```

Run: `python3 tools/validate_assets.py`
Expected: `OK — 13 assets, 0 preference records`

- [ ] **Step 6: Commit**

```bash
git add assets/preferences.json tools/validate_assets.py tools/test_validate_assets.py
git commit -m "feat(assets): preference memory scaffold + validator coverage"
```

---

### Task 4: Spike — SharePoint binary fetch → Figma `upload_assets` round trip

Gating step for Task 5: proves which fetch path works. Live MCP work, one test image, throwaway Figma artifacts.

**Files:**
- Create: `docs/superpowers/specs/2026-06-11-import-spike-result.md` (one-page result note; its conclusion is copied into the command file in Task 5)

- [ ] **Step 1: Load the MS365 + Figma tools**

One ToolSearch call: `select:mcp__claude_ai_Microsoft_365__sharepoint_search,mcp__claude_ai_Microsoft_365__sharepoint_folder_search,mcp__claude_ai_Microsoft_365__read_resource,mcp__figma__upload_assets`

- [ ] **Step 2: Find one test image in SharePoint**

Call `sharepoint_search` with a term certain to hit imagery (e.g. `purifier png` or `lifestyle jpg`). Record what comes back: file name, and crucially whether results carry a fetchable resource URI / download URL or only a web link.

- [ ] **Step 3: Try to fetch the binary**

Try, in order, stopping at the first success:
1. `read_resource` on the result's resource URI — does it return image bytes/base64?
2. If the result exposes a direct `@microsoft.graph.downloadUrl` or similar pre-authenticated URL: `curl -o "$CLAUDE_JOB_DIR/tmp/spike-test-image.jpg" "<url>"` and check `file "$CLAUDE_JOB_DIR/tmp/spike-test-image.jpg"` reports an image.
3. If neither works → **Path B confirmed**: ask the user for their locally synced OneDrive/SharePoint root (e.g. `~/Library/CloudStorage/OneDrive-SharedLibraries-…`), `find` an image file there, and use that as the fetch path.

- [ ] **Step 4: Upload the fetched image to Figma**

Call `mcp__figma__upload_assets` with the local file from Step 3, targeting file `GkUiwJTK5Xi65AKw4MOjTL`. Then verify visually with `get_screenshot` on the created node. Note the node's page placement behavior (which page it lands on, returned nodeId) — Task 5 needs to know whether uploads can target the Brand Assets page directly or must be moved there via `use_figma` afterwards.

- [ ] **Step 5: Clean up and write the result note**

Delete the spike node in Figma (via `use_figma`: `(await figma.getNodeByIdAsync("<id>")).remove()`). Write `docs/superpowers/specs/2026-06-11-import-spike-result.md` stating: which fetch path works (A: MCP `read_resource` binaries / A2: download-URL + curl / B: synced-folder fallback), the exact tool/URL pattern used, and where `upload_assets` places nodes. No "TBD" — record what was actually observed.

- [ ] **Step 6: Commit**

```bash
git add docs/superpowers/specs/2026-06-11-import-spike-result.md
git commit -m "docs(spike): SharePoint->Figma image round-trip result"
```

---

### Task 5: `/import-assets` command

**Files:**
- Create: `.claude/commands/import-assets.md`

- [ ] **Step 1: Write the command file**

Create `.claude/commands/import-assets.md` with the content below. **Replace the `## Fetch path` section body with the actual spike result from Task 4** (the text below shows the Path A wording; if the spike proved Path B, write the synced-folder instructions instead — the spike note has the specifics).

````markdown
# Import Assets from SharePoint

Search SharePoint for brand imagery, curate it visually in Figma, and index the keepers into `assets/library.json` (v2 schema).

## Usage
```
/import-assets <search terms | folder path>
```

## Fetch path
<!-- Spike result (docs/superpowers/specs/2026-06-11-import-spike-result.md): -->
Fetch binaries via <PATH PROVEN IN TASK 4 — exact tool/URL pattern from the spike note>.
Set `source.type` accordingly: `"sharepoint"` (MCP/download-URL fetch) or `"onedrive-sync"` (synced local folder).

## Important: Load skills and tools first
- Invoke the `figma:figma-use` skill before any `use_figma` call (mandatory).
- Load MCP tools in ONE ToolSearch call: `select:mcp__claude_ai_Microsoft_365__sharepoint_search,mcp__claude_ai_Microsoft_365__sharepoint_folder_search,mcp__claude_ai_Microsoft_365__read_resource,mcp__figma__upload_assets,mcp__figma__get_screenshot`

## Process

### Step 1: Find candidates
Search SharePoint with the user's terms (`sharepoint_search`; use `sharepoint_folder_search` when given a folder path). Image files only (jpg/jpeg/png/webp). Collect name + path + fetch handle per result.

**Dedupe:** read `assets/library.json`; drop any candidate whose path matches an existing `source.path`. List skipped duplicates in the final report only — do not re-offer them.

If zero candidates remain, report that and stop.

### Step 2: Fetch binaries
Fetch every remaining candidate to a temp dir (per the Fetch path section above). Discard non-image or zero-byte files.

### Step 3: Stage the Import inbox in Figma
Upload ALL candidates via `upload_assets` into file `GkUiwJTK5Xi65AKw4MOjTL`. Then with `use_figma`, arrange them in an **"Import inbox"** section on the Brand Assets page (`51124:14`), placed to the RIGHT of existing content (find `maxX` of existing children first):
- Grid of cards, 480px wide each (height per aspect), 4 per row, 48px gaps.
- Each card gets a label text node above it: `A1`, `A2`, `A3`, … plus the source filename at 14px gray below the label.
- Wrap the whole grid in a frame named `Import inbox — <date>`.

### Step 4: Curate (visual keep/skip)
`get_screenshot` the inbox frame and show it. Ask the user which to keep via AskUserQuestion (multiSelect over the labels, or free-form "keep A1, A3, B2"). **Never ask the user to judge by filename/path/size — the screenshot is the decision surface.**

### Step 5: Index keepers, delete skips
For each keeper, in `use_figma` + `get_screenshot` passes:
1. Rename the node to a kebab-case SEO-style asset key (descriptive: subject-product-context, e.g. `spirit-purifier-kitchen-lifestyle`). Move it out of the inbox frame into the Brand Assets page layout.
2. Measure `width`/`height` → `aspect` (2 decimals), derive `orientation` (square = 0.9–1.1).
3. Look at its screenshot and write: a one-sentence visual `description`, `tags`, `tone` (light/dark/mixed), `subject` (center/left/right/top/bottom), `suitability` (subset of hero/full-bleed/card/detail/texture; full-bleed needs atmospheric width AND high quality), `quality` (high/medium/low from visible sharpness at 2x).

Delete every skipped node, then delete the empty inbox frame.

### Step 6: Write the library and validate
Add each keeper to `assets/library.json` under `assets`:
```json
"<asset-key>": {
  "nodeId": "<figma node id>",
  "tags": [...],
  "description": "...",
  "source": { "type": "<fetch path type>", "path": "<sharepoint or local path>", "importedAt": "<YYYY-MM-DD>" },
  "visual": { "aspect": 0.0, "orientation": "...", "tone": "...", "subject": "...", "suitability": [...], "quality": "..." }
}
```
Run `python3 tools/validate_assets.py` — must end `OK`. If it fails, fix the entries and re-run; never leave the library red.

### Step 7: Report
```
Import complete.
Searched: "<terms>" — N candidates (M duplicates skipped)
Kept: K assets
  - spirit-purifier-kitchen-lifestyle (landscape 1.50, light, hero/full-bleed/card)
  - ...
Skipped: N-K (deleted from Figma)
Library: python3 tools/validate_assets.py → OK — <total> assets
```
````

- [ ] **Step 2: Verify with a live dry run**

Run `/import-assets <terms the user suggests>` end-to-end with a small batch (3–6 images). Confirm: inbox grid renders and screenshots legibly; keep/skip works from the screenshot alone; keepers land in the library with valid v2 entries; skips and the inbox frame are gone from Figma; `python3 tools/validate_assets.py` ends `OK`.

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/import-assets.md assets/library.json
git commit -m "feat(import): /import-assets — SharePoint search, Figma import inbox, vision indexing"
```

---

### Task 6: `/sync-assets` adopts schema v2

**Files:**
- Modify: `.claude/commands/sync-assets.md`

- [ ] **Step 1: Update the command file**

In `.claude/commands/sync-assets.md`:

1. Replace Step 3's "ask the user to provide tags and a short description" with the vision-index procedure (same as `/import-assets` Step 5): for each NEW asset, `get_screenshot` the node, measure w/h via `use_figma`, and write `description`, `tags`, and the full `visual` block yourself; ask the user only to confirm/adjust. New assets get `"source": { "type": "figma" }`.
2. Replace the Step 4 format block with the v2 entry format (copy the JSON block from `/import-assets` Step 6, with `source.type: "figma"` and no `path`).
3. Add to Step 4: existing assets keep their current `visual`/`source` untouched; only NEW assets are vision-indexed.
4. Add a final line to Step 5: `Run python3 tools/validate_assets.py — must end OK.`

- [ ] **Step 2: Verify**

Run `/sync-assets` once. Expected: "0 new assets" (nothing new on the page) and the validator line runs green — proving the command executes cleanly against the v2 library.

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/sync-assets.md
git commit -m "feat(sync-assets): adopt v2 schema + vision indexing for new assets"
```

---

### Task 7: Generator image intelligence (§5d rewrite)

**Files:**
- Modify: `.claude/commands/generate-presentation.md` (replace section "### 5d. Image Placement"; extend "## Step 6: Verify and Report")

- [ ] **Step 1: Replace §5d**

Replace the entire `### 5d. Image Placement` section (from the heading to just before `### 5e.`) with:

````markdown
### 5d. Image Placement (vision-indexed)

Image choice is a two-stage match against `assets/library.json` (v2: every asset carries a `visual` block), with preference boosts from `assets/preferences.json`. If the library is empty, skip image placement and note that `/import-assets` or `/sync-assets` should be run first.

#### 5d.1 Rank candidates per image slot

For each entry in the template's `imageSlots`:

1. **Semantic score (0–3):** compare the slide's title/topic/keywords against each asset's `tags` + `description`. 3 = direct subject match (slide about Spirit → asset tagged `spirit`); 2 = same family (any purifier asset for a purifier-range slide); 1 = generic brand-fit only (lifestyle/texture); 0 = unrelated. Discard 0s.
2. **Geometric filter (hard pass/fail):**
   - Slot aspect: from the registry entry's `w`/`h` when present (e.g. split-portrait 900×1023 → 0.88); otherwise by `size` tier: `small` ≈ 0.8–1.3, `medium` ≈ 1.0–1.6, `large` ≈ 1.4–1.9; `background-image` roles = 1.78 (full slide).
   - PASS when the asset's `visual.aspect` is within ±25% of the slot aspect, OR `visual.subject` is `center` (center-subject images crop safely under FILL).
   - `background-image` / hero roles additionally require `full-bleed` or `hero` in `visual.suitability` AND `visual.quality == "high"`.
   - Card/cell slots require at least one of `card`/`detail`/`hero` in `suitability`.
3. **Preference boost (tie-breaker):** read `assets/preferences.json → imagePicks`. +1 to an asset `chosen` for a similar context (same role or topic family); −1 when `rejected` in ≥2 similar contexts. Boosts never rescue a geometric FAIL.
4. **Rank** passing candidates by semantic score + boost. Top pick is applied now; the next 2–3 become the alternates strip in Curated mode (Step 5.5).

#### 5d.2 Apply with tone/subject rules

Copy the fill from the asset node to the slot (same page-switch pattern as before), forcing FILL:

```javascript
const assetPage = figma.root.children.find(p => p.id === "ASSET_PAGE_ID");
await figma.setCurrentPageAsync(assetPage);
const assetNode = await figma.getNodeByIdAsync("ASSET_NODE_ID");
const fills = JSON.parse(JSON.stringify(assetNode.fills));
for (const f of fills) if (f.type === "IMAGE") f.scaleMode = "FILL";

const outputPage = figma.root.children.find(p => p.id === "OUTPUT_PAGE_ID");
await figma.setCurrentPageAsync(outputPage);
const target = clone.findOne(n => n.name === "SLOT_NAME");  // or by role/position per registry note
target.fills = fills;
```

On image-overlay templates (`full-bleed-hero`, `full-bleed-tech-hero`, `cover-with-product`):
- Text variant follows the asset's `visual.tone`: `light` image → dark text (`isDark: false` chrome), `dark`/`mixed` → light text (`isDark: true`).
- Prefer candidates whose `visual.subject` keeps the bottom-left title zone clear (`right`/`top` best; `bottom`/`left` allowed only if nothing better passes — flag for Step 6 QA legibility check).

#### 5d.3 No-placeholder gate (REQUIRED)

A FIG placeholder must NEVER survive into the final deck. If ranking leaves any required image slot without a passing candidate, do not build the image template — **re-route the slide to its text-first equivalent** and record the re-route for the Step 6 summary:

| Image template | Text-first re-route |
|---|---|
| `pillar-grid-4up-image` | `template-bento4` |
| `pillar-grid-3up-*` | `template-bento3` |
| `pillar-grid-large-image` | `template-bento6` |
| `bento-mix-center-hero` | `template-bento5` |
| `full-bleed-hero` / `full-bleed-tech-hero` | `template-chapter-left` |
| `cover-with-product` | `template-title-subtitle-left` |
| `split-portrait` | `template-info-left-middle` |
| `template-product-2` / `-3` | `template-bento2` / `-bento3` |
| `bento-3up-delivery` | `template-bento3` |
| `template-info-Nbullets` | same template, image slots hidden (`optionalSlots`) + re-anchor (5e) |
| anything else | nearest no-`imageSlots` template with the same item count |

**All-or-nothing per slide:** if a multi-slot template (e.g. 3 pillars) has passing candidates for only SOME slots, re-route anyway — a mix of real images and placeholders is worse than a clean text slide. Exception: slots listed in the template's `optionalSlots` may be hidden instead (then re-anchor per 5e).
````

- [ ] **Step 2: Extend Step 6 with the imagery QA gate**

In `## Step 6: Verify and Report`, replace item 1 (`Use get_screenshot on a few slides…`) with:

```markdown
1. **Imagery QA gate (REQUIRED):** `get_screenshot` EVERY slide that carries an image (placed asset or overlay). Check each against:
   - Real image present — no FIG placeholder survived (if one did, the 5d.3 gate was skipped: re-route the slide now).
   - Text legible over the image (overlay templates): title/meta readable against the actual pixels behind them. If not, flip the text variant per `visual.tone`, or swap to the next-ranked candidate and re-check.
   - No awkward crop: the subject isn't cut off by FILL cropping. If it is, swap to the next-ranked candidate (prefer `subject: center`) and re-check.
   Fix what is fixable; anything still failing goes in the summary as "needs manual attention" with the reason.
2. `get_screenshot` a few text-only slides as a spot check.
```

(Renumber the existing "Present a summary" item accordingly, and add a `Re-routed slides:` line to the summary template listing every 5d.3 re-route with its reason.)

- [ ] **Step 3: Verify by inspection**

Re-read the modified file top to bottom once: §5d references only fields that exist in the v2 schema (`aspect`, `orientation`, `tone`, `subject`, `suitability`, `quality`), the re-route table names only templates present in `templates/registry.json` (spot-check: `template-bento4`, `template-chapter-left`, `template-info-left-middle` all exist), and §5e/§5g cross-references still hold.

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/generate-presentation.md
git commit -m "feat(generator): vision-indexed image matching, tone-aware overlays, no-placeholder gate, imagery QA"
```

---

### Task 8: Curated generation mode

**Files:**
- Modify: `.claude/commands/generate-presentation.md` (Step 3: add Question 3; after "### Present the Slide Plan": curated branch; after §5 build sections: Steps 5.5/5.6)

- [ ] **Step 1: Add the review-mode question to Step 3**

After `### Question 2: Voice & Tone`, insert:

```markdown
### Question 3: Review mode

Ask: **"How do you want to review the deck?"**

Options:
- **Curated** — For ambiguous slides I render up to 3 layout alternatives you pick from; then every image slide gets an alternates strip for quick swaps before we finalize. This is the default.
- **Direct** — One-shot build, no review rounds (the previous behavior). For quick throwaway decks.

In Direct mode, skip Step 4.5, Step 5.5 and Step 5.6 entirely.
```

- [ ] **Step 2: Add the layout pass (Step 4.5)**

In `### Present the Slide Plan`, add at the end: "In **Curated mode**, the plan confirmation is lightweight (the real review happens on rendered slides in Step 4.5) — present the plan, apply any corrections, and continue without a blocking confirm."

Then insert a new section between Step 4 and Step 5:

````markdown
## Step 4.5: Layout pass (Curated mode only)

The curator judges finished, rendered slides — never template names.

1. **Variant count per slide (adaptive):** while matching in Step 4, score the top template candidates 1–10 for fit. A slide is **ambiguous** when the top two scores are within 2 points → build the top **3** candidates as alternatives. One clear answer → 1 variant. Always 1 variant for: covers, chapter dividers, closing slides, and product-pack clones (already-approved layouts).
2. **Build the review grid:** build every variant as a complete slide (full §5 build — text, images per §5d, chrome, audit). Position: slide i at x = i·2120; variant A (the recommendation) at y = 0, B at y = 1280, C at y = 2560. Frame names: `S04-A — pillar-grid-4up-image (recommended)`, `S04-B — template-bento4`, …
3. **Collect picks:** `get_screenshot` each ambiguous slide's column (or the grid in chunks) and show the curator. Ask per ambiguous slide via AskUserQuestion ("Slide 4: A, B, or C?") or accept compact chat answers ("4→B, 9→C, rest A"). Unmentioned slides default to A.
4. **Assemble the final deck row:** move each chosen variant to y = 0 at its slide x; rename sequentially (`Slide 04 — <title>`); refresh page numbers via `applyDeckChrome` (total = final slide count); DELETE all losing variants.
5. **Log every decision** per Step 5.6 — including default-A confirms (chosen = A's template, rejected = B's and C's).
````

- [ ] **Step 3: Add the image pass (Step 5.5) and preference logging (Step 5.6)**

Insert after the §5 build sections (before `## Step 6`):

````markdown
## Step 5.5: Image pass (Curated mode only)

After assembly, for every slide with `imageSlots` where §5d.1 ranked ≥2 passing candidates:

1. **Build the alternates strip** below the slide: for each runner-up (max 3), a rectangle 300px wide (height per the candidate's aspect) filled with the candidate image (FILL), at y = slide.y + 1180, laid out left-to-right with 32px gaps from the slide's x. Label each with a 24px text node: `S04-B`, `S04-C`, `S04-D`. Group strip + labels in a frame named `S04-alternates`. Slides whose slot had only one passing candidate get no strip.
2. **Collect swaps:** `get_screenshot` the deck row with strips; show the curator; accept "4 → C"-style answers (AskUserQuestion or chat). Unmentioned slides keep their top pick.
3. **Apply swaps:** copy the chosen alternate's fill onto the slide's slot per §5d.2 — including the tone rule: if the new image's `visual.tone` differs, flip the text variant to match.
4. **On final confirm:** DELETE every `S*-alternates` frame; re-run `auditSlide` on swapped slides; proceed to Step 6 (the imagery QA gate covers the swapped images too).

## Step 5.6: Log preferences (Curated mode only)

Append one record per curation decision to `assets/preferences.json` (create as `{"imagePicks": [], "templatePicks": []}` if missing):

```json
// layout pick (one per slide that had alternatives; confirming A counts)
{ "context": { "contentShape": "<e.g. '4 items, image-rich'>", "deck": "<deck label>" },
  "chosen": "<template name, 'custom', or 'product:<slug>/<role>'>",
  "rejected": ["<losing template names>"], "date": "<YYYY-MM-DD>" }

// image pick (one per slide that had a strip; keeping the top pick counts)
{ "context": { "role": "<slot role or template category>", "topic": "<slide topic>", "slot": "<imageSlot name/role>" },
  "chosen": "<winning assetKey>", "rejected": ["<losing assetKeys>"], "date": "<YYYY-MM-DD>" }
```

Then run `python3 tools/validate_assets.py` — must end `OK`. These records feed the §5d.1 preference boost and the Step 4 template tie-breaker on every future run.
````

- [ ] **Step 4: Wire the template-side preference read into Step 4**

In `### Matching Priority`, add a final paragraph after the numbered list:

```markdown
**Preference tie-breaker:** before finalizing each slide's template, check `assets/preferences.json → templatePicks` for records with a similar `contentShape`. A template repeatedly chosen (≥2) for similar content wins ties and close calls; one repeatedly rejected is demoted below its rivals. Preferences never override the structural rules above (item counts, content types) — they only settle close calls. In Curated mode this also reorders which 3 candidates become the A/B/C alternatives (most-preferred = A).
```

- [ ] **Step 5: Verify by inspection**

Re-read the full command file once in order, simulating a 5-slide curated run mentally: Step 3 asks 3 questions → Step 4 scores → Step 4.5 grid (positions don't collide: variants at y 0/1280/2560, strips later at y+1180 of the FINAL row — confirm assembled slides sit at y=0 so strips at y=1180 don't overlap anything) → Step 5.5 swaps → 5.6 log → Step 6 QA. Confirm Direct mode skips 4.5/5.5/5.6 cleanly and reduces to the previous pipeline.

- [ ] **Step 6: Commit**

```bash
git add .claude/commands/generate-presentation.md
git commit -m "feat(generator): curated mode — adaptive layout alternatives, image alternates strips, preference logging"
```

---

### Task 9: Documentation (CLAUDE.md)

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update the architecture + library sections**

In the `## Architecture` list, add after the `assets/library.json` line:

```markdown
- `assets/preferences.json` — Curation memory: every layout/image pick from Curated mode, read back as a ranking tie-breaker by the matchers
- `.claude/commands/import-assets.md` — Slash command: SharePoint search → Figma "Import inbox" visual curation → vision-indexed library entries
- `tools/validate_assets.py` — Regression gate for `assets/library.json` (v2) + `assets/preferences.json`
```

Update the `assets/library.json` line itself to:

```markdown
- `assets/library.json` — Brand + product image index, v2: every asset carries vision metadata (`visual`: aspect/orientation/tone/subject/suitability/quality) + `source` provenance
```

- [ ] **Step 2: Add a short "Image Pipeline" section**

Insert after the `## Design System` section:

```markdown
## Image Pipeline

- **Library v2**: every asset in `assets/library.json` is vision-indexed (see `visual` block) — the generator matches semantically (tags/description) then geometrically (aspect vs slot, suitability, quality). Gate: `python3 tools/validate_assets.py` (must end `OK`).
- **Import**: `/import-assets <terms>` searches SharePoint, stages candidates in a visual "Import inbox" grid on the Brand Assets page, and indexes the keepers. Curation is always visual — never by filename.
- **No-placeholder gate**: a slide with no passing image candidate is re-routed to a text-first template; FIG placeholders never ship.
- **Curated mode** (default in `/generate-presentation`): ambiguous slides get up to 3 rendered layout alternatives to pick from; image slides get alternates strips for instant swaps. Every pick is logged to `assets/preferences.json` and improves future ranking. `Direct` mode = one-shot build.
- Spec: `docs/superpowers/specs/2026-06-11-image-pipeline-design.md`.
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: image pipeline — library v2, /import-assets, curated mode"
```

---

### Task 10: End-to-end verification

Live run with the user. No code changes expected — fixes discovered here go back into the relevant task's files with their own commits.

**Files:**
- None (verification only; fixes amend earlier files)

- [ ] **Step 1: Full test suite green**

Run: `python3 -m pytest tools/ -v`
Expected: all pass (existing newsletter tests + 14 asset tests).
Run: `python3 tools/validate_assets.py && python3 tools/validate_products.py && python3 tools/validate_newsletters.py`
Expected: three `OK` lines.

- [ ] **Step 2: First real import batch**

Ask the user for 1–2 search terms covering imagery they actually need (e.g. lifestyle shots), run `/import-assets`, confirm the full loop: visual inbox → keep/skip → indexed entries → validator `OK`. Target: library grows past 20 assets so matching has real choice.

- [ ] **Step 3: Curated-mode dry run**

Ask the user for a small real PDF (5–10 slides, ideally mentioning a known product). Run `/generate-presentation` in Curated mode. Verify against the spec's test list:
- Layout grid renders; ambiguous slides show 3 real alternatives; covers/dividers/product clones show 1.
- Picks assemble into a clean deck row; losing variants gone.
- Alternates strips appear only where ≥2 candidates passed; swaps apply instantly; strips fully deleted on confirm (zero orphan frames on the page).
- Zero FIG placeholders anywhere; any re-routes listed in the summary.
- `assets/preferences.json` gained records; `python3 tools/validate_assets.py` ends `OK`.

- [ ] **Step 4: Preference round trip**

Re-run the same PDF in Direct mode. In the slide-plan reasoning, confirm at least one template or image choice cites a preference record from Step 3's run (boost applied). This proves the memory loop closes.

- [ ] **Step 5: Final commit & wrap**

Any fixes from steps 2–4 are committed against their task's files. Then follow the superpowers:finishing-a-development-branch skill to merge `worktree-image-pipeline-spec` back.

---

## Self-review notes

- **Spec coverage:** Part 1 → Tasks 1–2; Part 2 → Tasks 4–5; `/sync-assets` adoption → Task 6; Part 3 → Task 7; Part 4 → Task 8 (adaptive counts, grid, strips, modes); Part 5 → Tasks 3 + 8 (write path) + 7/8 (read path); spec's testing list → Task 10.
- **Known judgment calls baked in:** slot-aspect tiers in 5d.1 (small 0.8–1.3 / medium 1.0–1.6 / large 1.4–1.9) are derived from the registry's `size` vocabulary — adjust in place if real slots disagree; strip y-offset 1180 assumes assembled slides at y=0 (set in Step 4.5.4).
- **Type consistency:** `visual` field names (`aspect`, `orientation`, `tone`, `subject`, `suitability`, `quality`) and enums match across validator (Task 1), backfill (Task 2), import (Task 5), sync (Task 6), and §5d (Task 7). Preference record shapes in Task 3 fixtures match Task 8 Step 5.6 templates (`context`/`chosen`/`rejected`/`date`; `custom` and `product:<slug>/<role>` escapes covered by the validator).
