"""Slide 26 -- Outdoor Stations. Figma node 63150:218."""

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, add_rounded_rect, add_label_with_mark, FONT_REGULAR, FONT_MEDIUM, FONT_SEMIBOLD


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater Stations", "26/33")

    add_text(
        slide, 48, 115, 1205, 90,
        [[("Outdoor stations.", FONT_SEMIBOLD, 64, "#27272a", 1.1)]],
    )
    add_text(
        slide, 1282, 115, 590, 100,
        [[("Pure water for outdoor venues, public spaces, hotels, and golf courses. Built for any climate.", FONT_MEDIUM, 28, "#71717a", 1.34)]],
    )

    # Left card -- Flow Station 3 (plain outdoors version)
    add_rounded_rect(slide, 48, 287, 896, 745, "#f4f4f5", 32)
    add_label_with_mark(
        slide, 96, 335, "Flow Station 3", FONT_MEDIUM, 24, "#2563eb",
        "™", FONT_REGULAR, 12, w=800, h=45, line_spacing=1.34,
    )
    add_text(
        slide, 96, 379, 800, 145,
        [
            {"runs": [("Built for the outdoors", FONT_SEMIBOLD, 36, "#27272a", 1.15)], "space_after_px": 16},
            {"runs": [("Delivers pure, chilled water on demand. All day, all year round.", FONT_MEDIUM, 24, "#52525b", 1.34)]},
        ],
    )
    add_picture(slide, f"{assets_dir}/slide_26/left_device.png", 276, 287, 668, 745)

    # Right card -- Flow Station 3 Media (screen version)
    add_rounded_rect(slide, 976, 287, 896, 745, "#f4f4f5", 32)
    add_picture(slide, f"{assets_dir}/slide_26/right_device.png", 1024, 287, 848, 745)
    add_label_with_mark(
        slide, 1024, 335, "Flow Station 3 Media", FONT_MEDIUM, 24, "#2563eb",
        "™", FONT_REGULAR, 12, w=800, h=45, line_spacing=1.34,
    )
    add_text(
        slide, 1024, 379, 800, 145,
        [
            {"runs": [("Add a screen", FONT_SEMIBOLD, 36, "#27272a", 1.15)], "space_after_px": 16},
            {"runs": [("A screen turns every refill into an opportunity to inform or advertise.", FONT_MEDIUM, 24, "#52525b", 1.34)]},
        ],
    )
    add_picture(slide, f"{assets_dir}/slide_26/right_screen.png", 1573, 435, 218, 394)

    return slide
