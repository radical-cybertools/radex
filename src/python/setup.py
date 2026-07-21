from setuptools import setup, Extension
from Cython.Build import build_ext
import pathlib
import os
import numpy

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent.parent
PY_SRC = HERE / "src"
CPP_SRC = ROOT / "src/cpp"

core = Extension(
    "radex",
    sources=[
        os.fspath(PY_SRC / "Client.pyx"),
        os.fspath(CPP_SRC / "client.cpp"),
        os.fspath(CPP_SRC / "dragon.cpp"),
    ],
    include_dirs=[
        os.fspath(ROOT / "include"),
        os.environ["DRAGON_INCLUDE_DIR"],
        numpy.get_include(),
    ],
    library_dirs=[
        os.environ["DRAGON_LIB_DIR"],
    ],
    libraries=[
        "dragon"
    ],
    language="c++",
    extra_compile_args=["-std=c++17"],
)

if __name__ == "__main__":
    setup(
        cmdclass={
            "build_ext": build_ext,
        },
        ext_modules=[core]
    )
