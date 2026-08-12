"""
Assembles the full Bluewater 2026 deck as an editable PowerPoint file.

Each slide's content lives in its own module under tools/pptx_slides/, built with
the shared helpers in tools/pptx_core.py (see that module's docstring for the
text-vs-image reconstruction strategy and the shadow/line-spacing fixes baked in).

Usage: python3 tools/export_pptx.py <assets_dir> <out_path.pptx>
  assets_dir must contain a subfolder per slide (assets_dir/slide_02/*.png, etc.)
  holding the images referenced by that slide's module.
"""

import sys
import importlib
from pptx import Presentation

from tools.pptx_core import px, SLIDE_W_PX, SLIDE_H_PX

# Canonical slide order (33 slides). Figma has a couple of stale/duplicate frames
# not part of the numbered sequence ("Slide 07" x2 leftovers at x=0,y=0, and a
# mislabeled "Slide 17 — Pro" frame that is actually slide 19) -- excluded here.
SLIDE_MODULES = [
    "slide_01_cover",
    "slide_02_who_we_are",
    "slide_03_bluewater_group",
    "slide_04_key_stats",
    "slide_05_our_clients",
    "slide_06_st_andrews_home_of_golf",
    "slide_07_st_andrews_what_we_delivered",
    "slide_08_chapter_our_technology",
    "slide_09_filtration_spectrum",
    "slide_10_superiorosmosis_technology",
    "slide_11_chapter_our_extracts",
    "slide_12_made_in_sweden",
    "slide_13_extract_range",
    "slide_14_why_consistency_matters",
    "slide_15_chapter_purifiers",
    "slide_16_purifiers_three_options",
    "slide_17_cleone",
    "slide_18_spirit",
    "slide_19_pro",
    "slide_20_chapter_bluewater_stations",
    "slide_21_kitchen_station",
    "slide_22_restaurant_station",
    "slide_23_beverage_station",
    "slide_24_cafe_station",
    "slide_25_freestanding_indoor_stations",
    "slide_26_outdoor_stations",
    "slide_27_house_station",
    "slide_28_emergency_station",
    "slide_29_chapter_bluewater_bottles",
    "slide_30_glass_bottles",
    "slide_31_steel_bottles",
    "slide_32_customise_bottle",
    "slide_33_closing",
]


def main():
    assets_dir = sys.argv[1] if len(sys.argv) > 1 else "/tmp/pptx_assets"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "/tmp/bluewater_deck.pptx"

    prs = Presentation()
    prs.slide_width = px(SLIDE_W_PX)
    prs.slide_height = px(SLIDE_H_PX)

    built, missing = [], []
    for name in SLIDE_MODULES:
        try:
            mod = importlib.import_module(f"tools.pptx_slides.{name}")
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
