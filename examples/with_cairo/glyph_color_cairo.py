#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------------------------------------------------------------------

 pycairo/cairocffi-based glyph-color example - Copyright 2017 Hin-Tak Leung
 Distributed under the terms of the new BSD license.

 rewrite of the numply,matplotlib-based example from Nicolas P. Rougier
 - The two side-glyphs are positioned only roughly equivalently.

-----------------------------------------------------------------------------

Glyph colored rendering (with outline)

2019-11-26: by Suzumizaki-Kimitaka(鈴見咲 君高)
 - Whole codes are put into :func:`run` function.
 - Automatic trying to import cairocffi when pycairo not exists.
 - Skip showing saved image when PIL/Pillow is not installed.
 - Reformat code to meet PEP8.
"""
from freetype import *

# using Matrix class from Cairo, instead of FreeType's
try:
    from cairo import Context, ImageSurface, FORMAT_ARGB32, SurfacePattern, FILTER_BEST, Matrix
except ImportError:
    from cairocffi import Context, ImageSurface, FORMAT_ARGB32, SurfacePattern, FILTER_BEST, Matrix
from bitmap_to_surface import make_image_surface


def run():
    face = Face('../Vera.ttf')
    face.set_char_size(96 * 64)

    # Outline
    flags = FT_LOAD_DEFAULT | FT_LOAD_NO_BITMAP
    face.load_char('S', flags)
    slot = face.glyph
    glyph = slot.get_glyph()
    stroker = Stroker()
    stroker.set(64, FT_STROKER_LINECAP_ROUND, FT_STROKER_LINEJOIN_ROUND, 0)
    glyph.stroke(stroker, True)
    del stroker
    blyph = glyph.to_bitmap(FT_RENDER_MODE_NORMAL, Vector(0, 0), True)
    bitmap = blyph.bitmap
    widthZ, rowsZ, pitch = bitmap.width, bitmap.rows, bitmap.pitch
    Z = make_image_surface(bitmap)

    # Plain
    flags = FT_LOAD_RENDER
    face.load_char('S', flags)
    bitmap = face.glyph.bitmap
    widthF, rowsF, pitch = bitmap.width, bitmap.rows, bitmap.pitch
    F = make_image_surface(bitmap)

    # Draw
    surface = ImageSurface(FORMAT_ARGB32, 1200, 500)
    ctx = Context(surface)

    # fill background as gray
    ctx.rectangle(0, 0, 1200, 500)
    ctx.set_source_rgb(0.5, 0.5, 0.5)
    ctx.fill()

    # use the stroked font's size as scale, as it is likely slightly larger
    scale = 400.0 / rowsZ

    # draw bitmap first
    ctx.set_source_surface(F, 0, 0)
    patternF = ctx.get_source()
    SurfacePattern.set_filter(patternF, FILTER_BEST)

    scalematrix = Matrix()
    scalematrix.scale(1.0 / scale, 1.0 / scale)
    scalematrix.translate(-(600.0 - widthF * scale / 2.0), -50)
    patternF.set_matrix(scalematrix)
    ctx.set_source_rgb(1, 1, 0)
    ctx.mask(patternF)
    ctx.fill()

    scalematrix.translate(+400, 0)
    patternF.set_matrix(scalematrix)
    ctx.mask(patternF)
    ctx.fill()

    # stroke on top
    ctx.set_source_surface(Z, 0, 0)
    patternZ = ctx.get_source()
    SurfacePattern.set_filter(patternZ, FILTER_BEST)

    scalematrix = Matrix()
    scalematrix.scale(1.0 / scale, 1.0 / scale)
    scalematrix.translate(-(600.0 - widthZ * scale / 2.0), -50)
    patternZ.set_matrix(scalematrix)
    ctx.set_source_rgb(1, 0, 0)
    ctx.mask(patternZ)
    ctx.fill()

    scalematrix.translate(-400, 0)
    patternZ.set_matrix(scalematrix)
    ctx.mask(patternZ)
    ctx.fill()

    surface.flush()
    image_name = "glyph_color_cairo.png"
    surface.write_to_png(image_name)
    try:
        from PIL import Image
        print("Displaying saved " + image_name + "...")
        Image.open(image_name).show()
    except ImportError:
        print(image_name + " saved.")


if __name__ == '__main__':
    run()
