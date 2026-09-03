import shutil

import pytest


@pytest.fixture(scope="session")
def _requires_redis_server():
    if shutil.which("redis-server") is None:
        pytest.skip("redis-server binary not found on PATH")
    yield


@pytest.fixture(scope="session")
def _requires_dragon_runtime():
    try:
        import dragon  # noqa: F401
        from dragon.globalservices.api_setup import get_gs_ret_cuid

        get_gs_ret_cuid()
    except Exception:
        in_dragon_session = False
    else:
        in_dragon_session = True

    if not in_dragon_session:
        pytest.skip(
            "Dragon session not detected! Try running with `dragon -s -- -m pytest`?"
        )
    yield
