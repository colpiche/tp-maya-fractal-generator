import maya.cmds as mc
import random


ORIGIN = [0, 0, 0]
FRACTAL_TYPES = ["Center cube", "Menger sponge", "Sierpinki pyramid"]


def clear_viewport():
    shapes = mc.ls(type="transform")
    mc.delete(shapes)


def generate_random_colors_list(list_lenght):
    color_list = []

    for i in range(list_lenght):
        color = []

        for j in range(3):
            random.seed()
            color.append(random.random())

        color_list.append(color)

    return color_list


def generate_fractal(fractal_type, size, generations, is_colorized=False, color_list=[]):

    if fractal_type == FRACTAL_TYPES[0]:
        y = compute_center_cube_fractal_offset(size, generations)
        print(y)
        generate_center_cube_fractal(
            [ORIGIN[0], y, ORIGIN[2]],
            size,
            generations,
            is_colorized,
            color_list
        )
    elif fractal_type == FRACTAL_TYPES[1]:
        generate_menger_sponge([ORIGIN[0], size / 2, ORIGIN[2]], size, generations)
    elif fractal_type == FRACTAL_TYPES[2]:
        generate_sierpinski_pyramid([ORIGIN[0], size / 2.84, ORIGIN[2]], size, generations)


def compute_center_cube_fractal_offset(size, generations):
    offset = 0

    for i in range(generations):
        offset = offset + size / 2
        size = size / 2

    return offset


def generate_center_cube_fractal(center, size, generation, is_colorized=False, color_list=[]):
    x, y, z = center
    generation -= 1

    if generation < 0:
        return

    if not mc.ls("center_cube", type="transform"):
        main_grp = mc.createNode("transform", name="center_cube")
    else:
        main_grp = mc.ls("center_cube", type="transform")

    if not mc.ls(f"gen{generation}", type="transform"):
        grp = mc.createNode("transform", name=f"gen{generation}")
        mc.parent(grp, main_grp)
    else:
        grp = mc.ls(f"gen{generation}", type="transform")

    shape = mc.polyCube(
        constructionHistory=False,
        name=f"cube_gen{generation}_",
        width=size,
        height=size,
        depth=size
    )[0]
    mc.setAttr(f"{shape}.translate", *center)

    if is_colorized is True:
        mc.polyColorPerVertex(shape, rgb=color_list[generation], colorDisplayOption=True)

    mc.parent(shape, grp)
    next_size = size / 2
    offset = size / 4 + next_size / 2
    right = [x + offset, y, z]
    left = [x - offset, y, z]
    front = [x, y + offset, z]
    back = [x, y - offset, z]
    top = [x, y, z + offset]
    bottom = [x, y, z - offset]
    generate_center_cube_fractal(right, next_size, generation, is_colorized, color_list)
    generate_center_cube_fractal(left, next_size, generation, is_colorized, color_list)
    generate_center_cube_fractal(front, next_size, generation, is_colorized, color_list)
    generate_center_cube_fractal(back, next_size, generation, is_colorized, color_list)
    generate_center_cube_fractal(top, next_size, generation, is_colorized, color_list)
    generate_center_cube_fractal(bottom, next_size, generation, is_colorized, color_list)


def generate_menger_sponge(center, size, generation, recursion_level=0):
    x, y, z = center

    if not mc.ls("menger_sponge", type="transform"):
        grp = mc.createNode("transform", name="menger_sponge")
    else:
        grp = mc.ls("menger_sponge", type="transform")

    if recursion_level == generation:
        shape = mc.polyCube(w=size, h=size, d=size)
        mc.move(x, y, z)
        mc.parent(shape, grp)
    else:
        size = size / 3.0
        for i in range(-1, 2):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    sum = abs(i) + abs(j) + abs(k)

                    if (sum and sum != 1):
                        generate_menger_sponge(
                            [x + i * size, y + j * size, z + k * size],
                            size,
                            generation,
                            recursion_level + 1
                        )


def generate_sierpinski_pyramid(center, size, generation, recursion_level=0):
    x, y, z = center

    if not mc.ls("sierpinski_pyramid", type="transform"):
        grp = mc.createNode("transform", name="sierpinski_pyramid")
    else:
        grp = mc.ls("sierpinski_pyramid", type="transform")

    if recursion_level == generation:
        shape = mc.polyPyramid(w=size)
        mc.move(x, y, z)
        mc.rotate(0, '45deg', 0)
        mc.parent(shape, grp)
    else:
        r = size / 4.0
        height = size / 2.84
        childs = [
            [0, height/2, 0],
            [r, -height/2, r],
            [r, -height/2, -r],
            [-r, -height/2, r],
            [-r, -height/2, -r]
        ]

        for c in childs:
            generate_sierpinski_pyramid(
                [x + c[0], y + c[1], z + c[2]],
                size / 2,
                generation,
                recursion_level + 1
            )
