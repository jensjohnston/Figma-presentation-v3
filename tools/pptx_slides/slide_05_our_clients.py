"""Slide 05 -- Our Clients. Figma node 63148:131.

3x3 logo garden. Each cell (including the "lululemon" wordmark, a brand mark rather
than editable body copy) is flattened as a single image straight from Figma -- this
sidesteps reconstructing the Four Seasons logo, which alone is built from 90+ vector
fill paths in the source file. Cells have no visible card background in Figma (no bg
color on the cell nodes), so no add_rounded_rect is drawn behind them.
"""

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, FONT_SEMIBOLD
from pptx.enum.text import PP_ALIGN

CELL_W = 587
CELL_H = 227
GAP = 32
COL_X = [48, 48 + CELL_W + GAP, 48 + 2 * (CELL_W + GAP)]
ROW_Y = [287, 287 + CELL_H + GAP, 287 + 2 * (CELL_H + GAP)]

CELLS = [
    "cell_1_w_hotels.png", "cell_2_volvo.png", "cell_3_four_seasons.png",
    "cell_4_pga_tour.png", "cell_5_apple.png", "cell_6_equinox.png",
    "cell_7_lululemon.png", "cell_8_red_bull.png", "cell_9_airbnb.png",
]


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater", "05/33")

    add_text(
        slide, 48, 115, 1824, 50,
        [[("Brands drinking Bluewater.", FONT_SEMIBOLD, 40, "#18181b", 1.1)]],
        align=PP_ALIGN.CENTER,
    )

    for i, filename in enumerate(CELLS):
        row, col = divmod(i, 3)
        add_picture(slide, f"{assets_dir}/slide_05/{filename}", COL_X[col], ROW_Y[row], CELL_W, CELL_H)

    return slide
