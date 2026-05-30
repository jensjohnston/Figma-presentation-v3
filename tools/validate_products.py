#!/usr/bin/env python3
"""Validate products/registry.json against the product-pack contract.

Regression gate for the product content library. Checks that every product
has the required fields, every slide uses a known role + unique nodeId, and
every image assetKey resolves in assets/library.json.
"""
import json, sys, pathlib

ROLES = {"hero", "key-specs", "how-it-works", "value-prop", "comparison",
         "pricing", "sustainability", "use-case", "cta"}


def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    reg = json.load(open(root / "products" / "registry.json"))
    lib = json.load(open(root / "assets" / "library.json"))
    asset_keys = set(lib.get("assets", {}))
    errors = []
    products = reg.get("products", {})
    if not products:
        errors.append("no products defined")
    for slug, p in products.items():
        for field in ("displayName", "pageId", "aliases", "slides"):
            if field not in p:
                errors.append(f"{slug}: missing '{field}'")
        if not isinstance(p.get("aliases"), list) or not p.get("aliases"):
            errors.append(f"{slug}: aliases must be a non-empty list")
        seen_nodes = set()
        for i, s in enumerate(p.get("slides", [])):
            for field in ("role", "nodeId", "matchHints", "slots"):
                if field not in s:
                    errors.append(f"{slug}.slides[{i}]: missing '{field}'")
            if s.get("role") not in ROLES:
                errors.append(f"{slug}.slides[{i}]: bad role {s.get('role')!r}")
            if s.get("nodeId") in seen_nodes:
                errors.append(f"{slug}.slides[{i}]: duplicate nodeId {s.get('nodeId')}")
            seen_nodes.add(s.get("nodeId"))
        for j, img in enumerate(p.get("images", [])):
            key = img.get("assetKey")
            if key not in asset_keys:
                errors.append(f"{slug}.images[{j}]: assetKey {key!r} not in assets/library.json")
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print(f"OK — {len(products)} products, "
          f"{sum(len(p.get('slides', [])) for p in products.values())} slides")


if __name__ == "__main__":
    main()
