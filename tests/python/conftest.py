import dataclasses
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
    yield _ROOT / "build"


@pytest.fixture(scope="session")
def _radex_include_dir():
    yield _ROOT / "include"


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


@pytest.fixture(scope="function")
def random_np_value(np_dtype):
    rng = np.random.default_rng()
    if np.issubdtype(np_dtype, np.integer):
        value = rng.integers(0, 100, dtype=np_dtype)
    else:
        value = np_dtype(rng.random(dtype=np_dtype))
    yield value


@pytest.fixture(
    scope="function",
    params=[
        pytest.param(args, id=f"shape={args[0]}-size={args[1]}")
        for args in [
            (10, (10,)),
            (10, (5, 2)),
            (10, (2, 5)),
            (24, (24,)),
            (24, (6, 4)),
            (24, (3, 8)),
            (24, (12, 2)),
            (24, (4, 3, 2)),
            (24, (2, 4, 3)),
            (24, (2, 2, 3, 2)),
            (36, (9, 2, 2)),
            (36, (3, 2, 2, 3)),
        ]
    ],
)
def random_np_tensor(np_dtype, request):
    size, shape = request.param
    yield np.arange(size, dtype=np_dtype).reshape(shape)


@dataclasses.dataclass(frozen=True)
class MyPickleable:
    some_str: str
    some_int: int


@dataclasses.dataclass(frozen=True)
class MyPickleable2:
    some_float: float


@pytest.fixture(
    scope="function",
    params=[
        pytest.param(picklable, id=f"{picklable=}")
        for picklable in [
            MyPickleable("spam", 123),
            MyPickleable("eggs", 0),
            MyPickleable("ham", -72),
            MyPickleable2(1.23),
            MyPickleable2(-98.7),
        ]
    ],
)
def random_picklable(request):
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
                f"-L{os.fspath(_radex_lib_dir)}",
                f"-Wl,-rpath={os.fspath(_radex_lib_dir)}",
                f"-l{_radex_lib_name}",
                "-o",
                os.fspath(bin_path),
                *extra_compile_args,
                os.fspath(src_file),
            ]
        )
        return bin_path

    yield _compile
