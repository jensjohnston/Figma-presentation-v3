"""Slide 24 -- Cafe Station. Figma node 63132:431."""

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, add_rect, add_label_with_mark, FONT_REGULAR, FONT_MEDIUM, FONT_SEMIBOLD


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater Stations", "24/33")

    # Full-bleed studio photo (kettle, faucet, espresso machine, tablet stand),
    # then the tablet's screen content composited on top: a flat placeholder
    # rect behind the actual app screenshot, matching Figma's z-order.
    add_picture(slide, f"{assets_dir}/slide_24/background.png", 0, 0, 1920, 1080)
    add_rect(slide, 138, 509, 249, 369, "#efedee")
    add_picture(slide, f"{assets_dir}/slide_24/app_screenshot.png", 132, 495, 261, 397)

    add_label_with_mark(
        slide, 48, 115, "Café Station 1", FONT_MEDIUM, 32, "#fa7317",
        "™", FONT_REGULAR, 16, w=400, h=45, line_spacing=1.1,
    )

    add_text(
        slide, 48, 162, 1083, 90,
        [[("The water your beans deserve.", FONT_SEMIBOLD, 64, "#18181b", 1.1)]],
    )

    add_text(
        slide, 1478, 115, 395, 100,
        [[("Precision-mineralized water for exceptional coffee. Infused with Coffee Rock minerals.", FONT_MEDIUM, 28, "#3f3f46", 1.34)]],
    )

    return slide
