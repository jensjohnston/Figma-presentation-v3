"""Slide 12 -- Made in Sweden. Figma node 63239:2."""

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, FONT_MEDIUM, FONT_SEMIBOLD


def build(prs, assets_dir):
    slide = new_slide(prs)

    # Full-bleed background photo with its 20%-black overlay already baked in
    # (screenshot of node 63132:1353, which is a real isolable frame containing both
    # the photo and the dark scrim as children -- unlike slide 11's fill-on-frame case).
    add_picture(slide, f"{assets_dir}/slide_12/background.png", 0, 0, 1920, 1080)

    add_meta(slide, "Bluewater Technology", "12/33")

    add_text(
        slide, 48, 115, 720, 170,
        [
            [("Bluewater extracts.", FONT_SEMIBOLD, 64, "#ffffff", 1.1)],
            [("Made in Sweden.", FONT_SEMIBOLD, 64, "#ffffff", 1.1)],
        ],
    )

    add_text(
        slide, 1168, 667, 705, 130,
        [[(
            "Every extract is built on science. Each formula is precision-engineered "
            "for the best possible beverage experience, from the glass to the cup.",
            FONT_MEDIUM, 32, "#ffffff", 1.25,
        )]],
    )

    return slide
