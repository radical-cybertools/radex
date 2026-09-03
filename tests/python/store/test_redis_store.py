import asyncio
import time

import pytest

import radex.store.redis_store as redis_store_module
from radex.store.base import StoreStartupError, StoreState
from radex.store.redis_store import RedisStore


@pytest.mark.redis
async def test_zero_arg_local_roundtrip(_requires_redis_server):
    store = RedisStore()
    await store.start()
    try:
        assert store.state is StoreState.READY
        eps = store.endpoints
        assert len(eps) == 1
        assert eps[0].host == "localhost"
        assert await store.ready() is True
    finally:
        await store.shutdown()
    assert store.state is StoreState.SHUTDOWN


@pytest.mark.redis
async def test_multi_node_concurrent_launch(_requires_redis_server):
    single = RedisStore()
    t0 = time.monotonic()
    await single.start()
    single_elapsed = time.monotonic() - t0
    await single.shutdown()

    store = RedisStore(hosts=["localhost"] * 4)
    t0 = time.monotonic()
    await store.start()
    multi_elapsed = time.monotonic() - t0
    try:
        eps = store.endpoints
        assert len(eps) == 4
        assert len({ep.port for ep in eps}) == 4
        assert await store.ready() is True
        # Loose bound: concurrent launch of 4 nodes should be nowhere near
        # 4x a single node's startup time.
        assert multi_elapsed < 3 * max(single_elapsed, 0.5)
    finally:
        await store.shutdown()


@pytest.mark.redis
async def test_partial_failure_rolls_back_all_nodes(
    _requires_redis_server, monkeypatch
):
    store = RedisStore(hosts=["localhost"] * 3, startup_timeout=1.0, poll_interval=0.05)
    seen: dict[tuple[str, int], int] = {}
    orig_ping = RedisStore._ping

    async def fake_ping(self, host, port):
        key = (host, port)
        if key not in seen:
            seen[key] = len(seen)
        if seen[key] == 1:
            return False
        return await orig_ping(self, host, port)

    monkeypatch.setattr(RedisStore, "_ping", fake_ping)

    with pytest.raises(StoreStartupError):
        await store.start()

    assert store.state is StoreState.FAILED
    assert store._processes == {}


async def test_terminate_then_kill_after_grace_period():
    store = RedisStore(shutdown_grace_period=0.05)

    class _StubProc:
        def __init__(self):
            self.returncode = None
            self.terminate_called = False
            self.kill_called = False

        def terminate(self):
            self.terminate_called = True

        def kill(self):
            self.kill_called = True
            self.returncode = -9

        async def wait(self):
            if not self.kill_called:
                await asyncio.sleep(9999)
            return self.returncode

    proc = _StubProc()
    await store._terminate_one(proc)
    assert proc.terminate_called is True
    assert proc.kill_called is True


async def test_terminate_one_skips_already_exited_process():
    store = RedisStore()

    class _ExitedProc:
        returncode = 0

        def terminate(self):
            raise AssertionError("should not be called")

        def kill(self):
            raise AssertionError("should not be called")

        async def wait(self):
            raise AssertionError("should not be called")

    await store._terminate_one(_ExitedProc())


@pytest.mark.redis
async def test_client_raises_import_error_without_redis_py(
    _requires_redis_server, monkeypatch
):
    monkeypatch.setattr(redis_store_module, "redis", None)
    store = RedisStore()
    await store.start()
    try:
        with pytest.raises(ImportError):
            store.client()
    finally:
        await store.shutdown()


@pytest.mark.redis
async def test_client_pings_real_node(_requires_redis_server):
    if redis_store_module.redis is None:
        pytest.skip("redis-py not installed")
    store = RedisStore()
    await store.start()
    try:
        client = store.client()
        assert client.ping() is True
    finally:
        await store.shutdown()
