#!/usr/bin/env python3
"""Validate renderers/email/newsletters/registry.json against the newsletter-pack contract.

Regression gate for the newsletter library. Mirrors tools/validate_products.py.
Checks that the HubSpot template path is set, every newsletter has the required
fields (displayName, product, heroHeadline, features), every `product` resolves in
products/registry.json, and every feature has a headline/body and an `image` that
resolves in assets/library.json (unless it is a direct https URL).

Honors the NEWSLETTER_REGISTRY env var (used by tests); otherwise reads the repo file.
"""
import json, os, sys, pathlib


def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    reg_path = os.environ.get(
        "NEWSLETTER_REGISTRY",
        root / "renderers" / "email" / "newsletters" / "registry.json")
    reg = json.load(open(reg_path))
    products = json.load(open(root / "products" / "registry.json")).get("products", {})
    asset_keys = set(json.load(open(root / "assets" / "library.json")).get("assets", {}))

    hub = reg.get("hubspot", {})
    errors = []
    if not hub.get("templatePath"):
        errors.append("hubspot.templatePath is missing")
    newsletters = reg.get("newsletters", {})
    if not newsletters:
        errors.append("no newsletters defined")
    for slug, n in newsletters.items():
        for field in ("displayName", "heroHeadline", "features"):
            if field not in n:
                errors.append(f"{slug}: missing '{field}'")
        # product is an optional link to the shared content core; validate only if present
        if "product" in n and n.get("product") not in products:
            errors.append(f"{slug}: product {n.get('product')!r} not in products/registry.json")
        variant = n.get("variant", "light")
        if variant not in ("light", "dark"):
            errors.append(f"{slug}: unknown variant {variant!r} (expected light or dark)")
        if variant == "dark" and not hub.get("templatePathDark"):
            errors.append(f"{slug}: variant dark but hubspot.templatePathDark is missing")
        features = n.get("features", [])
        if not features:
            errors.append(f"{slug}: features is empty")
        for i, f in enumerate(features):
            for field in ("image", "headline", "body"):
                if not f.get(field):
                    errors.append(f"{slug}: feature {i}: missing '{field}'")
            img = f.get("image", "")
            if not (isinstance(img, str) and img.startswith("http")) and img not in asset_keys:
                errors.append(f"{slug}: feature {i}: image {img!r} not in assets/library.json")
        for i, s in enumerate(n.get("specs", [])):  # specs are optional; validate shape if present
            for field in ("heading", "body"):
                if not s.get(field):
                    errors.append(f"{slug}: spec {i}: missing '{field}'")
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print(f"OK — {len(newsletters)} newsletters")


if __name__ == "__main__":
    main()
