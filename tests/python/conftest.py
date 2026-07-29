import os
import pathlib
import shutil
import subprocess

import numpy as np
import pytest

_SUPPORTED_NP_DTYPES = {
    np.int32: "int",
    np.int64: "long",
    np.float32: "float",
    np.float64: "double",
}

_HERE = pathlib.Path(__file__).parent.absolute()
_ROOT = _HERE.parent.parent


@pytest.fixture(scope="session")
def _radex_lib_dir():
    yield _ROOT / "install" / "lib"


@pytest.fixture(scope="session")
def _radex_include_dir():
    yield _ROOT / "install" / "include"


@pytest.fixture(scope="session")
def _radex_lib_name():
    yield "radex"


@pytest.fixture(scope="function")
def map_np_dtypes_to_cpp_types():
    yield _SUPPORTED_NP_DTYPES.copy()


@pytest.fixture(
    scope="function",
    params=[
        pytest.param(dtype, id=f"dtype={dtype.__name__}")
        for dtype in _SUPPORTED_NP_DTYPES
    ],
)
def np_dtype(request):
    yield request.param


@pytest.fixture
def _cpp_compiler_path():
    cpp_path = shutil.which(os.environ.get("CXX", "g++"))
    if cpp_path is None:
        pytest.fail("Could not find C++ compiler")
    yield cpp_path


@pytest.fixture
def cpp_type_name(np_dtype, map_np_dtypes_to_cpp_types):
    if (type_ := map_np_dtypes_to_cpp_types.get(np_dtype, None)) is None:
        pytest.fail(f"No C++ type provided for dtype {np_dtype.__name__}")
    return type_


@pytest.fixture
def cpp_compile(
    tmp_path, _cpp_compiler_path, _radex_include_dir, _radex_lib_dir, _radex_lib_name
):
    def _compile(src, src_name="src.cpp", bin_name="a.out", extra_compile_args=()):
        src_file = tmp_path / src_name
        src_file.touch()
        src_file.write_text(src)
        bin_path = tmp_path / bin_name
        subprocess.check_call(
            [
                os.fspath(_cpp_compiler_path),
                f"-I{os.fspath(_radex_include_dir)}",
                os.fspath(src_file),
                *extra_compile_args,
                f"-L{os.fspath(_radex_lib_dir)}",
                f"-Wl,-rpath={os.fspath(_radex_lib_dir)}",
                f"-l{_radex_lib_name}",
                "-o",
                os.fspath(bin_path),
            ]
        )
        return bin_path

    yield _compile
