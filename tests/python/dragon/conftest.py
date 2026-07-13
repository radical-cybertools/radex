import os

import dragon
import pytest
from dragon.data.ddict import DDict
from dragon.globalservices.api_setup import get_gs_ret_cuid
from radex import DragonClient as Client


@pytest.fixture(scope="session")
def _requires_dragon_runtime():
    try:
        get_gs_ret_cuid()
    except Exception:
        in_dargon_session = False
    else:
        in_dargon_session = True

    if not in_dargon_session:
        pytest.skip(
            "Dragon session not detected!" "Try running with `dragon -s -- -m pytest`?"
        )
    yield


@pytest.fixture(scope="session")
def _dragon_include_dir():
    yield os.environ["DRAGON_INCLUDE_DIR"]


@pytest.fixture(scope="session")
def _dragon_lib_dir():
    yield os.environ["DRAGON_LIB_DIR"]


@pytest.fixture(scope="session")
def _dragon_compile_args(_dragon_include_dir, _dragon_lib_dir):
    yield [
        f"-I{os.fspath(_dragon_include_dir)}",
        f"-L{os.fspath(_dragon_lib_dir)}",
        f"-Wl,-rpath={os.fspath(_dragon_lib_dir)}",
        "-ldragon",
    ]


@pytest.fixture
def cpp_dragon_compile(cpp_compile, _dragon_compile_args):
    def _compile(*args, extra_compile_args=(), **kwargs):
        return cpp_compile(
            *args,
            **kwargs,
            extra_compile_args=[
                *_dragon_compile_args,
                *extra_compile_args,
            ],
        )

    yield _compile


@pytest.fixture(scope="session")
def _session_ddict(_requires_dragon_runtime):
    ddict = DDict(managers_per_node=1, n_nodes=1)
    yield ddict


@pytest.fixture(scope="function")
def ddict(_session_ddict):
    yield _session_ddict
    _session_ddict.clear()


@pytest.fixture(scope="function")
def client(ddict):
    yield Client(descriptor=ddict.serialize(), timeout=5)
