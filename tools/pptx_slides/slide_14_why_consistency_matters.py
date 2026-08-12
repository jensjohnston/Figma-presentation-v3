"""Slide 14 -- Why Consistency Matters. Figma node 63132:399."""

from tools.pptx_core import (
    new_slide, add_meta, add_text, add_picture, add_rounded_rect,
    FONT_MEDIUM, FONT_SEMIBOLD,
)


def _bullets(slide, x, y, items):
    add_text(
        slide, x, y, 600, 190,
        [{"runs": [(t, FONT_MEDIUM, 24, "#27272a", 1.34)]} for t in items],
    )


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater Technology", "14/33")

    add_text(
        slide, 48, 115, 900, 90,
        [[("Consistency matters.", FONT_SEMIBOLD, 64, "#18181b", 1.1)]],
    )
    add_text(
        slide, 1354, 115, 478, 90,
        [[("Inline mineralization sets Bluewater apart. Here's the difference it makes.", FONT_MEDIUM, 28, "#71717a", 1.34)]],
    )

    # Card 1 -- Standard mineral filters
    add_rounded_rect(slide, 48, 287, 896, 745, "#f4f4f5", 32)
    add_picture(slide, f"{assets_dir}/slide_14/standard_filters_photo.png", 49, 314, 895, 540)
    add_text(
        slide, 96, 335, 800, 55,
        [[("Standard mineral filters", FONT_SEMIBOLD, 36, "#27272a", 1.32)]],
    )
    _bullets(slide, 96, 796, [
        "Effectiveness drops over time",
        "Mineral levels decline",
        "Unstable TDS and pH",
        "Inconsistent taste",
    ])

    # Card 2 -- Bluewater in-line mineralization
    add_rounded_rect(slide, 976, 287, 896, 745, "#f4f4f5", 32)
    add_picture(slide, f"{assets_dir}/slide_14/bluewater_mineralization_photo.png", 977, 335, 894, 513)
    add_text(
        slide, 1024, 335, 800, 55,
        [[("Bluewater in-line mineralization", FONT_SEMIBOLD, 36, "#27272a", 1.32)]],
    )
    _bullets(slide, 1024, 796, [
        "Precise dosing with liquid minerals",
        "Stable mineral levels",
        "Controlled TDS and pH",
        "Same taste, wherever you are",
    ])

    return slide
