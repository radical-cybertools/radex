"""Locations of the RaDex C++ headers and libraries bundled with the package."""

import os
import pathlib

_HERE = pathlib.Path(__file__).parent.absolute()

__all__ = ["get_include", "get_lib_dir", "get_lib_name"]


def get_include():
	"""Return the directory containing the bundled RaDex headers."""
	return os.fspath(_HERE / "include")


def get_lib_dir():
	"""Return the directory containing the bundled RaDex libraries."""
	return os.fspath(_HERE / "lib")


def get_lib_name():
	"""Return the RaDex library name without the linker prefix or suffix."""
	return "radex"
