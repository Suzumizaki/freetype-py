# -*- encoding: utf-8 -*-
"""
FT_Bitmap to CAIRO_SURFACE_TYPE_IMAGE module
============================================
Copyright 2017 Hin-Tak Leung

FreeType is under FTL (BSD license with an advertising clause) or GPLv2+.
Cairo is under LGPLv2 or MPLv1.1.

Converting from Freetype's FT_Bitmap to Cairo's CAIRO_SURFACE_TYPE_IMAGE
Use :func:`make_image_surface()` .

Limitation: Surface.create_for_data is not in the "python 3, pycairo < 1.11" combo.

This is a heavily modified copy of a few routines from Lawrence D'Oliveiro[1],
adjusted for freetype-py, and bugfix/workaround for mono-rendering [2].

TODO: Look into using FreeType's FT_Bitmap_Convert() instead. However, libtiff
     is common enough, and probably not important.

[1] https://github.com/ldo/python_freetype
    https://github.com/ldo/python_freetype_examples

[2] https://github.com/ldo/python_freetype/issues/1
    https://github.com/ldo/python_freetype_examples/issues/1

2019-11-27: by Suzumizaki-Kimitaka(鈴見咲 君高)
 - Supports convertion from freetype.FT_PIXEL_MODE_BGRA to cairo.FORMAT_ARGB32.
 - Automatic trying to import cairocffi when pycairo not exists.
 - Using python code when libtiff cannot be loaded (for pre-built binary for Windows).
 - Reformat code to meet PEP8.
"""
from freetype import FT_PIXEL_MODE_MONO, FT_PIXEL_MODE_GRAY, FT_Pointer, FT_Bitmap
from array import array
from ctypes import cast, memmove, CDLL, c_void_p, c_int
from sys import byteorder

try:
    from cairo import ImageSurface, FORMAT_A1, FORMAT_A8, FORMAT_ARGB32
except ImportError:
    from cairocffi import ImageSurface, FORMAT_A1, FORMAT_A8, FORMAT_ARGB32

FT_PIXEL_MODE_BGRA = 7  # TODO: At 2019-11-27, freetype_py does not define this. see ft_pixel_modes.py.


def make_image_surface(bitmap, copy=True):
    if type(bitmap) == FT_Bitmap:
        # bare FT_Bitmap
        content = bitmap
    else:
        # wrapped Bitmap instance
        content = bitmap._FT_Bitmap
    # creates a Cairo ImageSurface containing (a copy of) the Bitmap pixels.
    if content.pixel_mode == FT_PIXEL_MODE_MONO:
        cairo_format = FORMAT_A1
    elif content.pixel_mode == FT_PIXEL_MODE_GRAY:
        cairo_format = FORMAT_A8
    elif content.pixel_mode == FT_PIXEL_MODE_BGRA:
        # Both freetype.FT_PIXEL_MODE_BGRA and cairo.FORMAT_ARGB32 uses
        # pre-multiplied alpha, so no fix is required.
        cairo_format = FORMAT_ARGB32
    else:
        raise NotImplementedError("unsupported bitmap format %d" % content.pixel_mode)
    src_pitch = content.pitch
    dst_pitch = ImageSurface.format_stride_for_width(cairo_format, content.width)
    if not copy and dst_pitch == src_pitch and content.buffer is not None:
        pixels = content.buffer
    else:
        pixels = to_array(content, content.pixel_mode, dst_pitch)
    result = ImageSurface.create_for_data(
        pixels, cairo_format,
        content.width, content.rows,
        dst_pitch)
    return result


def to_array(content, pixel_mode, dst_pitch=None):
    """returns a Python array object containing a copy of the Bitmap pixels."""
    if dst_pitch is None:
        dst_pitch = content.pitch
    buffer_size = content.rows * dst_pitch
    buffer = array("B", b"0" * buffer_size)
    dstaddr = buffer.buffer_info()[0]
    srcaddr = cast(content.buffer, FT_Pointer).value
    src_pitch = content.pitch
    if dst_pitch == src_pitch:
        memmove(dstaddr, srcaddr, buffer_size)
    else:
        # have to copy a row at a time
        if src_pitch < 0 or dst_pitch < 0:
            raise NotImplementedError("can't cope with negative bitmap pitch")
        assert dst_pitch > src_pitch
        for i in range(content.rows):
            memmove(dstaddr, srcaddr, src_pitch)
            dstaddr += dst_pitch
            srcaddr += src_pitch
    # swap the bit-order from freetype's (MSB) to cairo's (host order) if needed
    if byteorder == 'little' and pixel_mode == FT_PIXEL_MODE_MONO:
        # Even pillow/PIL itself requires libtiff, you should NOT consider it is assumed to be around.
        # Because prebuilt binary version exists especially for Windows.
        try:
            libtiff = CDLL("libtiff.so.5")
            libtiff.TIFFReverseBits.restype = None
            libtiff.TIFFReverseBits.argtypes = (c_void_p, c_int)
            libtiff.TIFFReverseBits(buffer.buffer_info()[0], buffer_size)
        except OSError:
            for idx in range(buffer_size):
                v, w = buffer[idx], 0
                for bit_idx in range(8):
                    w |= (0x80 >> bit_idx) if v & (1 << bit_idx) else 0
                buffer[idx] = w
    return buffer
