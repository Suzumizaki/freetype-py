#!python3
# -*- encoding: utf-8 -*-
"""Run all examples *_cairo.py

This code is licensed under the terms of the new or revised BSD license, as freetype-py is.

Make sure all of:
 - "cairo" C-library (means not Python) installed.
 - appropriate environment variable points "cairo".
 - "pycairo" or "cairocffi" is enabled on your python (installed by pip or like).
On Windows, as easist way at current, 2019-11:
  - install msys2 (https://www.msys2.org/), generally msys2-x86_64-yyyymmdd.exe.
  - at exiting installer WITHOUT starting terminal window or close it if opened.
  - run "MSYS2 MinGW 64-bit" from start icon and type that, make sure it, run.
  - do "pacman -Syu". close and redo if you are guided to close the window.
  - do "pacman -S mingw64/mingw-w64-x86_64-cairo".

    - for 32bit, "pacman -S mingw32/mingw-w64-i686-cairo" instead.

  - add "C:\msys64\mingw64\bin" to PATH environment variable.

    - or do "import os; os.environ['PATH'] += ';' + "<the path above>"  every time.
    - for 32bit, replace 64 to 32, but the former is about your PC, the latter is about executables.

  - install cairocffi, generally using "pip install cairocffi"

    - "cairocffi" seems better than "pycairo" unless you have any special reasons.
    - if you use PyCharm and failed from its preference, try "pip" from PyCharm's Ternimal.

2019-11-27: by 鈴見咲 君高(Suzumizaki-Kimitaka)
  - first version.
"""


def run_one(name):
    cn = name + '_cairo'
    exec('import ' + cn + '; print("running ' + cn + ' ..."); ' + cn + '.run()')


def run_all():
    names = (
        'hello_world example_1 glyph_outline glyph_mono_plus_alpha '
        'glyph_color glyph_vector glyph_vector_2 glyph_lcd '
        'emoji_color wordle').split()
    for n in names:
        run_one(n)


if __name__ == '__main__':
    import os
    # os.environ['PATH'] += ';' + 'C:\\msys64\\mingw64\\bin'
    os.chdir(os.path.dirname(__file__))
    run_all()
