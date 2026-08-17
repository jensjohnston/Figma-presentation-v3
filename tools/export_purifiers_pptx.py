"""
Assembles the "Bluewater Purifiers" 9-slide deck as an editable PowerPoint file.

Sibling to tools/export_pptx.py, built from the separate canvas "All purifiers"
(Figma node 61219:14889) rather than the main 33-slide "Bluewater 2026" deck.
Each slide's content lives in tools/pptx_slides_purifiers/, using the same
shared helpers in tools/pptx_core.py.

Usage: python3 tools/export_purifiers_pptx.py <assets_dir> <out_path.pptx>
  assets_dir must contain a subfolder per slide (assets_dir/slide_02/*.png, etc.)
  holding the images referenced by that slide's module.
"""

import sys
import importlib
from pptx import Presentation

from tools.pptx_core import px, SLIDE_W_PX, SLIDE_H_PX

# Canonical slide order, read off each frame's x-position on the Figma canvas
# (left to right = intended build order): cover -> filtration spectrum -> tech
# deep-dive -> three-option overview -> Cleone/Spirit/Pro profiles -> lineup
# recap -> comparison table.
SLIDE_MODULES = [
    "slide_01_cover",
    "slide_02_filtration_spectrum",
    "slide_03_tech_superiorosmosis",
    "slide_04_options_3up",
    "slide_05_profile_cleone",
    "slide_06_profile_spirit",
    "slide_07_profile_pro",
    "slide_08_lineup",
    "slide_09_comparison_table",
]


def main():
    assets_dir = sys.argv[1] if len(sys.argv) > 1 else "/tmp/pptx_purifiers_assets"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "/tmp/bluewater_purifiers_deck.pptx"

    prs = Presentation()
    prs.slide_width = px(SLIDE_W_PX)
    prs.slide_height = px(SLIDE_H_PX)

    built, missing = [], []
    for name in SLIDE_MODULES:
        try:
            mod = importlib.import_module(f"tools.pptx_slides_purifiers.{name}")
        except ModuleNotFoundError:
            missing.append(name)
            continue
        mod.build(prs, assets_dir)
        built.append(name)

    prs.save(out_path)
    print(f"Saved {out_path} ({len(built)}/{len(SLIDE_MODULES)} slides)")
    if missing:
        print("Missing modules (skipped):")
        for name in missing:
            print(f"  - {name}")


if __name__ == "__main__":
    main()
