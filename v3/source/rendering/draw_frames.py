import os
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageFont

file_path = Path(os.path.realpath(__file__))
CURRENT_DIR = file_path.parent


def tile(im1, length, wide):
    dst = Image.new("RGB", (im1.width * wide, im1.height * length))
    for i in range(wide):
        for j in range(length):
            dst.paste(im1, (im1.width * i, im1.height * j))
    return dst


def one_frame(plant):
    images = {}
    for stage in ["growing", "blooming", "fruiting", "fruit", "dead"]:
        images[stage] = Image.open(
            CURRENT_DIR / ("sprites/" + plant.parameters["sprite"][stage])
        )
    # 32x32

    X = plant.field.shape["length"]
    Y = plant.field.shape["width"]
    # im_soil = Image.open(CURRENT_DIR / "sprites/soil.png")
    # image = tile(im_soil, X, Y)

    im_width, im_height = 64, 64
    image = Image.new("RGB", im_width * Y, im_height * X)
    for x in range(X):
        for y in range(Y):
            image.paste(
                images[plant.variables["stage"][x, y]],
                (im_width * y, im_height * x),
                mask=images[plant.variables["stage"][x, y]],
            )

    return image


# TODO: rewrite
def dashboard(stage_growth, nb_of_day, q_level, day, name_plant="corn"):
    length, wide = stage_growth.shape

    im_soil = Image.open(CURRENT_DIR / "sprites/soil.png")
    dashboard_picture = Image.new(
        "RGB",
        (
            im_soil.width * wide + im_soil.width * 9,
            im_soil.height * length + im_soil.height,
        ),
    )
    im_field = one_frame(stage_growth, name_plant)
    dashboard_picture.paste(im_field, (0, im_soil.height))
    d = ImageDraw.Draw(dashboard_picture)
    font = ImageFont.truetype("Gidole-Regular.ttf", size=500)
    d.text(
        (im_soil.width * (wide // 2), im_soil.height // 2),
        "Day: {}".format(day),
        font=font,
        fill="yellow",
    )

    rows = 4
    col = 3
    figure, axis = plt.subplots(rows, col, figsize=(100, 100))

    plt.tick_params(axis="x", labelsize=100)

    # For the quantity of water in the soil
    axis[0, 0].plot(np.arange(nb_of_day), q_level, linewidth=15)
    """axis[0, 0].spines['bottom'].set_linewidth(15)
    axis[0, 0].spines['left'].set_linewidth(15)"""
    axis[0, 0].set_title("q", fontsize=200)

    figure.canvas.draw()
    graphs = Image.frombytes(
        "RGB", figure.canvas.get_width_height(), figure.canvas.tostring_rgb()
    )
    dashboard_picture.paste(graphs, (im_soil.width * wide, im_soil.height))

    return dashboard_picture


"""table_growth = np.array([[3, 1, -1, 2, 2],
                         [1, 4, 1, 2, 2],
                         [1, 1, 4, 2, -1],
                         [-1, 1, 3, 2, 1],
                         [1, 1, 3, 2, 1],
                         [2, 3, 1, 1, 1],
                         [1, 2, 2, -1, 1],
                         [2, 1, 2, 1, 1]])
frame = one_frame(table_growth, 'corn')
frame.show()"""
# frame.save('first_field.png')
"""im1 = get_concat_h(im, im)
im1.show()"""
"""table_growth = np.array([[3, 1, -1, 2, 2],
                         [1, 4, 1, 2, 2],
                         [1, 1, 4, 2, -1],
                         [-1, 1, 3, 2, 1],
                         [1, 1, 3, 2, 1],
                         [2, 3, 1, 1, 1],
                         [1, 2, 2, -1, 1],
                         [2, 1, 2, 1, 1]])

nb_day = 100
q = np.arange(100)
q[:10] = [250, 236, 289, 284, 281, 275, 273, 279, 285, 290]

frame = dashboard(table_growth, nb_of_day=nb_day, q_level=q, day=10, name_plant='bean')
frame.save('test.png')
# frame.show()
"""
