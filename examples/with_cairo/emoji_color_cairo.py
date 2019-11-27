#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pycairo/cairocffi-based emoji-color example - Copyright 2017 Hin-Tak Leung
Distributed under the terms of the new BSD license.

This script demonstrates overlapping emojis.

Note: On Mac OS X before Sierra (10.12), change ttc->ttf;
      try Google's NotoColorEmoji.ttf at size 109 on Linux.

Limitation: Suface.get_data() is not in the "python 3, pycairo < 1.11" combo.

2019-11-26: by Suzumizaki-Kimitaka(鈴見咲 君高)
 - Automatic loading emoji font which possibly pre-installed on Windows.
 - Automatic trying to import cairocffi when pycairo not exists.
 - :code:`face.glyph.bitmap` does not need to meet :code:`width * 4` for now.
 - Whole codes are put into :func:`run` function.
 - Skip showing saved image when PIL/Pillow is not installed.
 - Reformat code to meet PEP8.
"""
import sys
import freetype

try:
    from cairo import ImageSurface, FORMAT_ARGB32, Context
except ImportError:
    from cairocffi import ImageSurface, FORMAT_ARGB32, Context
from bitmap_to_surface import make_image_surface


def run(path_or_stream=None):
    if path_or_stream:
        # Note: Current NotoColorEmoji seems not compatible
        #       with current freetype2 or freetype_py.
        # Original Note:
        # Not all char sizes are valid for emoji fonts;
        # Google's NotoColorEmoji only accept size 109 to get 136x128 bitmaps
        face = freetype.Face(path_or_stream)
        char_size = 109 * 64
    else:
        if sys.platform.startswith('win32'):
            face = freetype.Face('C:\\Windows\\Fonts\\seguiemj.ttf')
            char_size = 160 * 64
        elif sys.platform.startswith('darwin'):
            face = freetype.Face("/System/Library/Fonts/Apple Color Emoji.ttc")
            char_size = 160 * 64
        else:
            raise NotImplementedError('Sorry, automatic font loading supports only Windows or macOS.')

    face.set_char_size(char_size)
    if sys.maxunicode < 0x10000:
        target_char = u'😀'
        index = face.get_char_index(0x10000 + 0x400 * (ord(target_char[0]) - 0xd800) + ord(target_char[1]) - 0xdc00)
    else:
        index = face.get_char_index('😀')
    face.load_glyph(index, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_COLOR)
    bitmap = face.glyph.bitmap
    image_surface = make_image_surface(bitmap)
    width, rows = bitmap.width, bitmap.rows  # in pixels unit.

    # Both freetype.FT_PIXEL_MODE_BGRA and cairo.FORMAT_ARGB32 uses
    # pre-multiplied alpha, so no fix is required.
    surface = ImageSurface(FORMAT_ARGB32, 2 * width, rows)

    ctx = Context(surface)
    ctx.set_source_surface(image_surface, 0, 0)
    ctx.paint()
    ctx.set_source_surface(image_surface, width / 2, 0)
    ctx.paint()
    ctx.set_source_surface(image_surface, width, 0)
    ctx.paint()
    image_name = "emoji_color_cairo.png"
    surface.write_to_png(image_name)
    try:
        from PIL import Image
        print("Displaying saved " + image_name + "...")
        Image.open(image_name).show()
    except ImportError:
        print(image_name + " saved.")


if __name__ == '__main__':
    run()
