"""Slide 21 -- Kitchen Station. Figma node 63150:169."""

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, add_label_with_mark, FONT_MEDIUM, FONT_SEMIBOLD


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater Stations", "21/33")

    a = f"{assets_dir}/slide_21"

    add_picture(slide, f"{a}/background.png", 0, 0, 1920, 1080)

    add_label_with_mark(
        slide, 48, 115, "Kitchen Station 1", FONT_MEDIUM, 32, "#ffffff",
        "™", FONT_MEDIUM, 16, w=500, h=40, line_spacing=1.1,
    )

    add_text(
        slide, 48, 162, 837, 100,
        [[("Mineralized water at home.", FONT_SEMIBOLD, 64, "#ffffff", 1.1)]],
    )

    add_text(
        slide, 1348, 115, 524, 130,
        [
            [
                ("Kitchen Station 1", FONT_MEDIUM, 28, "#ffffff", 1.34),
                ("™", FONT_MEDIUM, 28, "#ffffff", 1.34),
                (" is the complete home water system. Pure water, mineralized with Liquid Rock. Controlled by you.", FONT_MEDIUM, 28, "#ffffff", 1.34),
            ]
        ],
    )

    return slide
