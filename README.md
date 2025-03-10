# cube2sphere [![PyPI version](https://badge.fury.io/py/cube2sphere.svg)](https://pypi.python.org/pypi/cube2sphere) [![PyPI](https://img.shields.io/pypi/pyversions/cube2sphere.svg)](https://pypi.python.org/pypi/cube2sphere)

`cube2sphere` is a Python script to map 6 cube (cubemap, skybox) faces
into an equirectangular (cylindrical projection, skysphere) map. See
also [`sphere2cube`](https://github.com/Xyene/sphere2cube).

This fork allows using the tool programmatically from other Python scripts,
without a detour through the command line.

## Usage (Command Line)

    $ cube2sphere -h
    usage: cube2sphere [-h] [-v] [-r <width> <height>] [-R <rx> <ry> <rz>]
                   [-o <path>] [-f <name>] [-b <path>] [-t <count>] [-V]
                   <front> <back> <right> <left> <top> <bottom>

    Maps 6 cube (cubemap, skybox) faces into an equirectangular (cylindrical
    projection, skysphere) map.

    positional arguments:
      <front>               source front cube face filename
      <back>                source back cube face filename
      <right>               source right cube face filename
      <left>                source left cube face filename
      <top>                 source top cube face filename
      <bottom>              source bottom cube face filename

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -r <width> <height>, --resolution <width> <height>
                            resolution for rendered map (defaults to 1024x512)
      -R <rx> <ry> <rz>, --rotation <rx> <ry> <rz>
                            rotation in degrees to apply before rendering map (z
                            is up)
      -o <path>, --output <path>
                            filename for rendered map (defaults to "out")
      -f <name>, --format <name>
                            format to use when saving map, i.e. "PNG" or "TGA"
      -b <path>, --blender-path <path>
                            filename of the Blender executable (defaults to
                            "blender")
      -t <count>, --threads <count>
                            number of threads to use when rendering (1-64)
      -V, --verbose         enable verbose logging

Supported output formats depend on the Blender installation, but will
generally include TGA, IRIS, JPEG, MOVIE, IRIZ, RAWTGA, AVIRAW, AVIJPEG,
PNG, BMP, and FRAMESERVER.

`cube2sphere` can be run in a headless environment (e.g., a server).

### Examples

If we wanted to stitch 6 cube faces named `${face}.jpg` into a 2048x1024
TGA equirectangular map, we could use the following command:

    $ cube2sphere front.jpg back.jpg right.jpg left.jpg top.jpg bottom.jpg -r 2048 1024 -fTGA -ostitched

This would generate `stitched0001.tga` in the working directory.

## Usage (Python)

```python
import cube2sphere

# Create a new cube2sphere instance
c2s = cube2sphere.Cube2Sphere(
    front='front.jpg',
    back='back.jpg',
    right='right.jpg',
    left='left.jpg',
    top='top.jpg',
    bottom='bottom.jpg',
    resolution=(2048, 1024),
    format='TGA',
    output='stitched',
    blender_path='blender',
    threads=4,
    verbose=True
)

# Convert the cube faces to a sphere
c2s.convert()
```

## Installation

`cube2sphere` can be easily installed with `pip`. It requires a Python 3 installation.

It assumes that [Blender](https://www.blender.org/) is installed and the `blender` executable is
listed in the system PATH environment variable. If it is not possible
for PATH to be edited (as in the case of an unprivileged user), the path
to the `blender` executable may instead be passed through the `-b` flag.

### Windows

Install Blender, and add `blender.exe` to `PATH`. Finally,

    pip install git+https://git.private.coffee/kumi/cube2sphere.git

### Linux

Most distributions come with Python 3 pre-installed. To install Blender
and `cube2sphere` on Debian-based systems, run:

    $ apt-get install blender
    $ pip install git+https://git.private.coffee/kumi/cube2sphere.git

### Mac OS X

Similar to Windows, install Blender, and add the `blender` executable
to `$PATH`. Then,

    $ pip install git+https://git.private.coffee/kumi/cube2sphere.git
