#!/usr/bin/env python3
"""Validate renderers/email/newsletters/registry.json against the newsletter-pack contract.

Regression gate for the newsletter library. Mirrors tools/validate_products.py.
Checks that the HubSpot template path is set, every newsletter has the required
fields, every slot key is in slotVocabulary, every `product` resolves in
products/registry.json, and every `heroAsset` resolves in assets/library.json.

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

    vocab = set(reg.get("slotVocabulary", []))
    errors = []
    if not reg.get("hubspot", {}).get("templatePath"):
        errors.append("hubspot.templatePath is missing")
    if not vocab:
        errors.append("slotVocabulary is empty")
    newsletters = reg.get("newsletters", {})
    if not newsletters:
        errors.append("no newsletters defined")
    for slug, n in newsletters.items():
        for field in ("displayName", "product", "heroAsset", "slots"):
            if field not in n:
                errors.append(f"{slug}: missing '{field}'")
        if n.get("product") not in products:
            errors.append(f"{slug}: product {n.get('product')!r} not in products/registry.json")
        if n.get("heroAsset") not in asset_keys:
            errors.append(f"{slug}: heroAsset {n.get('heroAsset')!r} not in assets/library.json")
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
