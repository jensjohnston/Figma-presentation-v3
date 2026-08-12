"""Slide 08 -- Chapter: Our Technology. Figma node 63132:366."""

from pptx.enum.text import MSO_ANCHOR

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, add_rect, FONT_SEMIBOLD


def build(prs, assets_dir):
    slide = new_slide(prs)

    # Full-bleed dark background (slide is on the dark #18181b canvas).
    add_rect(slide, 0, 0, 1920, 1080, "#18181b")

    add_meta(slide, "Bluewater Technology", "08/33")

    # Decorative glowing "SuperiorOsmosis" badge -- screenshot of node 63132:371 as
    # rendered on canvas (the box-shadow glow bleeds past its 995x995 layout box and
    # gets clipped by the slide edges on the right/top/bottom; left edge fades to
    # transparent, so Figma's exporter trimmed it to 971x1080, right-aligned to the
    # canvas edge). Includes the "SuperiorOsmosis(TM)" wordmark baked in as a
    # decorative gradient-fill motif.
    add_picture(slide, f"{assets_dir}/slide_08/circle_badge.png", 949, 0, 971, 1080)

    add_text(
        slide, 48, 0, 1824, 1080,
        [[("Our Technology.", FONT_SEMIBOLD, 120, "#ffffff", 1.0)]],
        anchor=MSO_ANCHOR.MIDDLE,
    )

    return slide
