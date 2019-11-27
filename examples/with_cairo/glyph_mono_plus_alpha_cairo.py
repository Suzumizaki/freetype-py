#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------------------------------------------------------------------

pycairo/cairocffi-based glyph-mono/alpha example - Copyright 2017 Hin-Tak Leung
Distributed under the terms of the new BSD license.

rewrite of the numply,matplotlib-based example from Nicolas P. Rougier
- Not immitating the upside-downness of glyph-monochrome/glyph-alpha

This script default to normal(8-bit) rendering, but render to mono
if any argument is specified.

-----------------------------------------------------------------------------
Glyph bitmap monochrome/alpha rendring

2019-11-26: by Suzumizaki-Kimitaka(鈴見咲 君高)
 - Whole codes are put into :func:`run` function.
 - Automatic trying to import cairocffi when pycairo not exists.
 - Skip showing saved image when PIL/Pillow is not installed.
 - Reformat code to meet PEP8.
"""
from freetype import *

# use Matrix() from Cairo instead of from Freetype
try:
    from cairo import Context, ImageSurface, FORMAT_ARGB32, SurfacePattern, FILTER_BEST, Matrix
except ImportError:
    from cairocffi import Context, ImageSurface, FORMAT_ARGB32, SurfacePattern, FILTER_BEST, Matrix
from bitmap_to_surface import make_image_surface


def run(load_target_normal=False):
    import sys

    face = Face('../Vera.ttf')
    face.set_char_size(48*64)

    if load_target_normal:
        # Normal(8-bit) Rendering
        face.load_char('S', FT_LOAD_RENDER |
                       FT_LOAD_TARGET_NORMAL)
    else:
        # Mono(1-bit) Rendering
        face.load_char('S', FT_LOAD_RENDER |
                       FT_LOAD_TARGET_MONO)

    width = face.glyph.bitmap.width
    rows = face.glyph.bitmap.rows

    glyph_surface = make_image_surface(face.glyph.bitmap)

    surface = ImageSurface(FORMAT_ARGB32, 800, 600)
    ctx = Context(surface)
    ctx.rectangle(0, 0, 800, 600)
    ctx.set_line_width(0)
    ctx.set_source_rgb(0.5, 0.5, 0.5)
    ctx.fill()
    #
    scale = 480.0 / rows
    ctx.set_source_surface(glyph_surface, 0, 0)
    pattern = ctx.get_source()
    SurfacePattern.set_filter(pattern, FILTER_BEST)
    scalematrix = Matrix()
    scalematrix.scale(1.0 / scale, 1.0 / scale)
    scalematrix.translate(-(400.0 - width * scale / 2.0), -60)
    pattern.set_matrix(scalematrix)
    ctx.set_source_rgb(0, 0, 1)
    ctx.mask(pattern)
    ctx.fill()
    surface.flush()
    image_name = "glyph_mono+alpha_cairo.png"
    surface.write_to_png(image_name)
    try:
        from PIL import Image
        print("Displaying saved " + image_name + "...")
        Image.open(image_name).show()
    except ImportError:
        print(image_name + " saved.")


if __name__ == '__main__':
    run()
