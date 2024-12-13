import argparse
import os
import sys
import subprocess
import math
from .version import __version__
from typing import Optional

try:
    from PIL import Image
except ImportError:
    Image = None


class Cube2Sphere:
    def __init__(
        self,
        front: os.PathLike,
        back: os.PathLike,
        left: os.PathLike,
        right: os.PathLike,
        top: os.PathLike,
        bottom: os.PathLike,
        resolution: Optional[tuple[int, int]] = (1024, 512),
        rotation: tuple[int, int, int] = (0, 0, 0),
        output: os.PathLike = "out",
        fmt: str = "TGA",
        blender_path: os.PathLike = "blender",
        threads: Optional[int] = None,
        verbose: bool = False,
    ):
        """Initializes the Cube2Sphere object.

        Args:
            front (os.PathLike): Path to the front face of the cube.
            back (os.PathLike): Path to the back face of the cube.
            left (os.PathLike): Path to the left face of the cube.
            right (os.PathLike): Path to the right face of the cube.
            top (os.PathLike): Path to the top face of the cube.
            bottom (os.PathLike): Path to the bottom face of the cube.
            resolution (tuple[int, int], optional): Resolution of the output image. Auto-detected if unspecified or set to (0, 0).
            rotation (tuple[int, int, int], optional): Rotation to apply before rendering the image. Defaults to (0, 0, 0).
            output (os.PathLike, optional): Path to save the output image. Defaults to "out".
            fmt (str, optional): Format of the output image. Defaults to "TGA".
            blender_path (os.PathLike, optional): Path to the Blender executable. Defaults to "blender".
            threads (Optional[int], optional): Number of threads to use when rendering. Defaults to None.
            verbose (bool, optional): Enable verbose logging. Defaults to False.
        """

        self.faces = {
            "front": front,
            "back": back,
            "left": left,
            "right": right,
            "top": top,
            "bottom": bottom,
        }
        self.resolution = resolution
        self.rotation = [math.radians(x) for x in rotation]
        self.output = (
            output if os.path.isabs(output) else os.path.join(os.getcwd(), output)
        )
        self.format = fmt
        self.blender_path = blender_path
        self.threads = threads
        self.verbose = verbose

    def validate(self) -> None:
        """Validates the input arguments.

        Raises:
            ValueError: If any of the cube faces are not valid files.
            ValueError: If the number of threads is out of range.
            ImportError: If Pillow is not installed and image resolution detection is required.
        """

        if not all(os.path.isfile(face) for face in self.faces.values()):
            raise ValueError("All cube faces must be valid files")

        if not self.resolution or self.resolution == (0, 0):
            if not Image:
                raise ImportError("Image resolution detection requires Pillow")

            front = self.faces["front"]
            with Image.open(front) as img:
                width, height = img.size
                self.resolution = (width * 4, height * 2)

        if self.threads and (self.threads < 1 or self.threads > 64):
            raise ValueError("Too many threads specified (range is 1-64)")

    def convert(self) -> None:
        """Converts the cube faces to a sphere.

        Raises:
            RuntimeError: If the Blender executable cannot be spawned.
            RuntimeError: If Blender exits with a non-zero return code.
        """
        self.validate()
        out = open(os.devnull, "w") if not self.verbose else None
        faces_paths = [self.absolute_path(face) for face in self.faces.values()]

        command = [
            self.blender_path,
            "-E",
            "CYCLES",
            "--background",
            "-noaudio",
            "-b",
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "projector.blend"
            ),
            "-o",
            self.output,
            "-F",
            self.format,
            "-x",
            "1",
            "-P",
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "blender_init.py"
            ),
        ]
        + (["-t", str(self.threads)] if self.threads else [])
        + [
            "--",
            *faces_paths,
            str(self.resolution[0]),
            str(self.resolution[1]),
            str(self.rotation[0]),
            str(self.rotation[1]),
            str(self.rotation[2]),
        ]

        if self.verbose:
            print("Running command:")
            print(" ".join(command))

        try:
            process = subprocess.Popen(
                command,
                stderr=out,
                stdout=out,
            )
        except Exception as e:
            raise RuntimeError("Error spawning blender executable") from e
        else:
            process.wait()
            if process.returncode:
                raise RuntimeError(
                    f"Blender exited with error code {process.returncode}"
                )

    def absolute_path(self, path: os.PathLike) -> os.PathLike:
        """Helper function to get the absolute path of a file.

        Args:
            path (os.PathLike): Path to the file.

        Returns:
            os.PathLike: Absolute path of the file.
        """
        return path if os.path.isabs(path) else os.path.join(os.getcwd(), path)


def main():
    """Main function to parse command line arguments and run the conversion."""

    parser = argparse.ArgumentParser(
        prog="cube2sphere",
        description="""
        Maps 6 cube (cubemap, skybox) faces into an equirectangular (cylindrical projection, skysphere) map.
    """,
    )

    for f in ["front", "back", "left", "right", "top", "bottom"]:
        parser.add_argument(
            f, type=str, metavar="<%s>" % f, help=f"source {f} cube face filename"
        )

    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        nargs=2,
        default=[0, 0],
        metavar=("<width>", "<height>"),
        help="resolution for rendered map (auto-detected if unspecified)",
    )
    parser.add_argument(
        "-R",
        "--rotation",
        type=int,
        nargs=3,
        default=[0, 0, 0],
        metavar=("<rx>", "<ry>", "<rz>"),
        help="rotation in degrees to apply before rendering map (z is up)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="out",
        metavar="<path>",
        help='filename for rendered map (defaults to "out")',
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        default="TGA",
        metavar="<name>",
        help='format to use when saving map, i.e. "PNG" or "TGA"',
    )
    parser.add_argument(
        "-b",
        "--blender-path",
        type=str,
        default="blender",
        metavar="<path>",
        help='filename of the Blender executable (defaults to "blender")',
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=None,
        metavar="<count>",
        help="number of threads to use when rendering (1-64)",
    )
    parser.add_argument(
        "-V", "--verbose", action="store_true", help="enable verbose logging"
    )

    args = parser.parse_args()

    try:
        cube2sphere = Cube2Sphere(
            front=args.front,
            back=args.back,
            left=args.left,
            right=args.right,
            top=args.top,
            bottom=args.bottom,
            resolution=args.resolution,
            rotation=args.rotation,
            output=args.output,
            fmt=args.format,
            blender_path=args.blender_path,
            threads=args.threads,
            verbose=args.verbose,
        )

        if Image is None:
            print("Warning: Pillow is not installed, image resolution detection is disabled")

        cube2sphere.convert()
    except Exception as e:
        parser.print_usage()
        print(f"cube2sphere: error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
