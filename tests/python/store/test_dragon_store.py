import pytest

from radex.store.base import StoreState, StoreTerminatedError
from radex.store.dragon_store import DragonStore

pytestmark = pytest.mark.usefixtures("_requires_dragon_runtime")


def test_wait_for_keys_false_raises():
    with pytest.raises(ValueError, match=r"wait_for_keys"):
        DragonStore(wait_for_keys=False)


def test_default_construction_does_not_raise():
    DragonStore()


async def test_start_ready_shutdown_roundtrip():
    store = DragonStore(managers_per_node=1, n_nodes=1)
    await store.start()
    try:
        assert store.state is StoreState.READY
        eps = store.endpoints
        assert len(eps) == 1
        assert eps[0].descriptor
        assert await store.ready() is True
    finally:
        await store.shutdown()
    assert store.state is StoreState.SHUTDOWN


async def test_client_roundtrip_put_get_scalar():
    from radex.handles.handles import IncomingHandle, OutgoingHandle

    store = DragonStore(managers_per_node=1, n_nodes=1)
    await store.start()
    try:
        client = store.client(timeout=5)
        client.put_scalar(OutgoingHandle("store-test-key"), 0.5)
        assert client.get_scalar(IncomingHandle("store-test-key")) == 0.5
    finally:
        await store.shutdown()


async def test_start_after_shutdown_raises():
    store = DragonStore(managers_per_node=1, n_nodes=1)
    await store.start()
    await store.shutdown()
    with pytest.raises(StoreTerminatedError):
        await store.start()


async def test_wait_false_is_noop_for_dragon():
    store = DragonStore(managers_per_node=1, n_nodes=1)
    await store.start(wait=False)
    try:
        assert store.state is StoreState.READY
        assert store.endpoints[0].descriptor
    finally:
        await store.shutdown()
