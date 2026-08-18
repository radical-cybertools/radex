import asyncio

import pytest

from radex.store.base import (
    Endpoint,
    Store,
    StoreNotReadyError,
    StoreStartupError,
    StoreState,
    StoreTerminatedError,
)


class _FakeEndpoint(Endpoint):
    def __init__(self, tag: str = "fake"):
        self.tag = tag

    def serialize(self) -> str:
        return self.tag

    def client(self, **kwargs):
        return {"tag": self.tag, **kwargs}


class _FakeStore(Store):
    def __init__(self, fail_start: bool = False, fail_ready: bool = False):
        super().__init__()
        self.fail_start = fail_start
        self.fail_ready = fail_ready
        self.start_calls = 0
        self.shutdown_calls = 0
        self.shutdown_seen_states = []

    async def _do_start(self, wait: bool):
        self.start_calls += 1
        if self.fail_start:
            raise RuntimeError("boom")
        return [_FakeEndpoint()]

    async def _do_shutdown(self) -> None:
        self.shutdown_calls += 1
        self.shutdown_seen_states.append(self.state)

    async def _do_ready(self) -> bool:
        return not self.fail_ready


async def test_endpoints_before_start_raises():
    store = _FakeStore()
    with pytest.raises(StoreNotReadyError):
        _ = store.endpoints


async def test_start_and_shutdown_return_self_for_fluent_usage():
    # Guards against `store = await RedisStore(...).start()` silently
    # assigning None -- start()/shutdown() must return the Store instance.
    store = await _FakeStore().start()
    assert isinstance(store, _FakeStore)
    assert store.state is StoreState.READY

    returned = await store.shutdown()
    assert returned is store
    assert store.state is StoreState.SHUTDOWN


async def test_start_then_endpoints():
    store = _FakeStore()
    await store.start()
    assert store.state is StoreState.READY
    eps = store.endpoints
    assert len(eps) == 1
    assert eps[0].serialize() == "fake"


async def test_repeated_start_is_idempotent():
    store = _FakeStore()
    await store.start()
    await store.start()
    await store.start()
    assert store.start_calls == 1


async def test_repeated_shutdown_is_idempotent():
    store = _FakeStore()
    await store.start()
    await store.shutdown()
    await store.shutdown()
    await store.shutdown()
    assert store.shutdown_calls == 1


async def test_shutdown_never_started_is_noop_but_calls_hook_once():
    store = _FakeStore()
    await store.shutdown()
    assert store.state is StoreState.SHUTDOWN
    assert store.shutdown_calls == 1
    assert store.shutdown_seen_states == [StoreState.CREATED]


async def test_start_after_shutdown_raises():
    store = _FakeStore()
    await store.start()
    await store.shutdown()
    with pytest.raises(StoreTerminatedError):
        await store.start()


async def test_failing_start_sets_failed_and_raises_with_cause():
    store = _FakeStore(fail_start=True)
    with pytest.raises(StoreStartupError) as excinfo:
        await store.start()
    assert store.state is StoreState.FAILED
    assert isinstance(excinfo.value.__cause__, RuntimeError)


async def test_start_after_failure_raises_terminated():
    store = _FakeStore(fail_start=True)
    with pytest.raises(StoreStartupError):
        await store.start()
    with pytest.raises(StoreTerminatedError):
        await store.start()


async def test_shutdown_after_failure_is_noop_and_invokes_hook_once():
    store = _FakeStore(fail_start=True)
    with pytest.raises(StoreStartupError):
        await store.start()
    await store.shutdown()
    assert store.state is StoreState.SHUTDOWN
    assert store.shutdown_calls == 1


async def test_store_client_delegates_and_gates_on_readiness():
    store = _FakeStore()
    with pytest.raises(StoreNotReadyError):
        store.client()
    await store.start()
    assert store.client(extra=1) == {"tag": "fake", "extra": 1}


async def test_ready_reflects_lifecycle():
    store = _FakeStore()
    assert await store.ready() is False
    await store.start()
    assert await store.ready() is True
    await store.shutdown()
    assert await store.ready() is False


async def test_concurrent_start_calls_do_start_once():
    store = _FakeStore()
    await asyncio.gather(store.start(), store.start(), store.start())
    assert store.start_calls == 1
    assert store.state is StoreState.READY
