"""Slide 22 -- Restaurant Station. Figma node 63150:175."""

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, add_rounded_rect, add_label_with_mark, FONT_MEDIUM, FONT_SEMIBOLD


def _bento_cell(slide, x, y, eyebrow, heading, body, photo_path):
    add_rounded_rect(slide, x, y, 896, 745, "#f4f4f5", 32)
    add_picture(slide, photo_path, x, 440, 896, 592, radius_px=32)
    add_label_with_mark(
        slide, x + 48, y + 48, eyebrow, FONT_MEDIUM, 24, "#2563eb",
        "™", FONT_MEDIUM, 12, w=800, h=24, line_spacing=1.34,
    )
    add_text(slide, x + 48, y + 96, 800, 41, [[(heading, FONT_SEMIBOLD, 36, "#27272a", 1.15)]])
    add_text(slide, x + 48, y + 153, 800, 42, [[(body, FONT_MEDIUM, 24, "#52525b", 1.34)]])


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater Stations", "22/33")

    a = f"{assets_dir}/slide_22"

    add_text(
        slide, 48, 115, 1205, 90,
        [[("For offices, cafés and restaurants.", FONT_SEMIBOLD, 64, "#27272a", 1.1)]],
    )
    add_text(
        slide, 1470, 115, 402, 90,
        [[("Premium water for restaurants, hotels, offices, gyms and spas.", FONT_MEDIUM, 28, "#71717a", 1.34)]],
    )

    _bento_cell(
        slide, 48, 287,
        "Restaurant Station 1", "Pure, still, mineralized water",
        "Autofill and Bluewater app. Control volumes with precision.",
        f"{a}/photo_left.png",
    )
    _bento_cell(
        slide, 976, 287,
        "Restaurant Station 2", "Add a chilled, sparkling option",
        "Autofill and Bluewater app. Control volumes with precision.",
        f"{a}/photo_right.png",
    )

    return slide
