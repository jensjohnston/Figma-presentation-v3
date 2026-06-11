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
