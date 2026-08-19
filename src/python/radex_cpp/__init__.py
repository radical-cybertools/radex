"""Locations of the RaDex C++ headers and libraries bundled with the package."""

import os
import pathlib

_HERE = pathlib.Path(__file__).parent.absolute()

__all__ = ["get_include", "get_lib_dir", "get_lib_name"]


def get_include():
    """Directory containing the ``radex/*.hpp`` headers, incl. ``build_config.hpp``."""
    return os.fspath(_HERE / "include")


def get_lib_dir():
    """Directory containing the bundled RaDex libraries."""
    return os.fspath(_HERE / "lib")


def get_lib_name():
    """Name to pass to the linker (i.e. the ``foo`` in ``-lfoo``)."""
    return "radex"
