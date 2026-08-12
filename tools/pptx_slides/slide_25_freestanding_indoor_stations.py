"""Slide 25 -- Free-standing Indoor Stations. Figma node 63150:194."""

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, add_rounded_rect, add_label_with_mark, FONT_REGULAR, FONT_MEDIUM, FONT_SEMIBOLD


def _bento_cell_text(slide, x, y, label, heading, body):
    add_text(
        slide, x, y, 800, 190,
        [
            {"runs": [(label, FONT_MEDIUM, 24, "#2563eb", 1.34)], "space_after_px": 16},
            {"runs": [(heading, FONT_SEMIBOLD, 36, "#27272a", 1.15)], "space_after_px": 16},
            {"runs": [(body, FONT_MEDIUM, 24, "#52525b", 1.34)]},
        ],
    )


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater Stations", "25/33")

    add_text(
        slide, 48, 115, 1205, 90,
        [[("Stand-alone water stations.", FONT_SEMIBOLD, 64, "#18181b", 1.1)]],
    )
    add_text(
        slide, 1408, 115, 464, 100,
        [[("High-capacity dispensing for gyms, studios, hotels and public spaces.", FONT_MEDIUM, 28, "#71717a", 1.34)]],
    )

    # Left card -- Bluewater Flow
    add_rounded_rect(slide, 48, 287, 896, 745, "#f4f4f5", 32)
    add_picture(slide, f"{assets_dir}/slide_25/card1_photo.png", 48, 547, 896, 485, radius_px=32)
    _bento_cell_text(slide, 96, 335, "Bluewater Flow", "Pure water with electrolytes", "7x purified water, electrolyte-enhanced, no waste. Hot water available.")

    # Right card -- Flow Station 2
    add_rounded_rect(slide, 976, 287, 896, 745, "#f4f4f5", 32)
    add_picture(slide, f"{assets_dir}/slide_25/card2_photo.png", 976, 547, 896, 485, radius_px=32)
    add_label_with_mark(
        slide, 1024, 335, "Flow Station 2", FONT_MEDIUM, 24, "#2563eb",
        "™", FONT_REGULAR, 12, w=800, h=45, line_spacing=1.34,
    )
    add_text(
        slide, 1024, 379, 800, 145,
        [
            {"runs": [("Customized beverages", FONT_SEMIBOLD, 36, "#27272a", 1.15)], "space_after_px": 16},
            {"runs": [("Design your beverage with our functional extracts and flavors.", FONT_MEDIUM, 24, "#52525b", 1.34)]},
        ],
    )

    return slide
