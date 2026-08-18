from setuptools import setup, Extension
from Cython.Build import cythonize, build_ext
import pathlib
import os
import numpy

HERE = pathlib.Path(".")
ROOT = pathlib.Path("../..")
PY_SRC = HERE / "src"
CPP_SRC = ROOT / "src/cpp"

radex_client_core = Extension(
    "radex.clients.core",
    language="c++",
    sources=[
        os.fspath(path)
        for path in (
            PY_SRC / "radex/clients/core.pyx",
            CPP_SRC / "client.cpp",
            CPP_SRC / "dragon.cpp",
            CPP_SRC / "smartredis.cpp",
        )
    ],
    include_dirs=[
        os.fspath(ROOT / "include"),
        os.environ["DRAGON_INCLUDE_DIR"],
        os.environ["SMARTREDIS_INCLUDE_DIR"],
        numpy.get_include(),
    ],
    library_dirs=[
        os.environ["DRAGON_LIB_DIR"],
        os.environ["SMARTREDIS_LIB_DIR"],
    ],
    libraries=[
        "dragon",
        "smartredis",
    ],
    extra_compile_args=["-std=c++17"],
)

radex_handles_handles = Extension(
    "radex.handles.handles",
    language="c++",
    sources=[
        os.fspath(path)
        for path in (
            PY_SRC / "radex/handles/handles.pyx",
            CPP_SRC / "handles.cpp",
        )
    ],
    include_dirs=[
        os.fspath(ROOT / "include"),
    ],
    extra_compile_args=["-std=c++17"],
)

if __name__ == "__main__":
    ORIGINAL_DIR = pathlib.Path(os.getcwd())
    os.chdir(pathlib.Path(__file__).parent)
    try:
        setup(
            cmdclass={
                "build_ext": build_ext,
            },
            ext_modules=cythonize(
                [
                    radex_client_core,
                    radex_handles_handles,
                ]
            ),
            package_dir={"": "src"},
        )
    finally:
        os.chdir(ORIGINAL_DIR)
