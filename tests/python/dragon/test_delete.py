import os
import sys

import pytest

from radex.handles.handles import IncomingHandle, OutgoingHandle


def _anon_memory_bytes():
    """The anonymous resident memory of this process, read from `/proc`."""
    with open("/proc/self/status") as status:
        for line in status:
            if line.startswith("RssAnon:"):
                return int(line.split()[1]) * 1024
    pytest.skip("`RssAnon` is not reported in `/proc/self/status`")


def test_delete_typed_item(client, random_np_value):
    key = "some-value-to-delete"
    client.put_scalar(OutgoingHandle(key), random_np_value)
    assert client.contains(key)

    client.delete_item(OutgoingHandle(key))

    assert not client.contains(key)
    assert not client.contains(f"meta::{key}")


def test_delete_raw_key(client, random_picklable):
    key = "some-object-to-delete"
    client.put_picklable(key, random_picklable)
    assert client.contains(key)

    client.delete_item(OutgoingHandle(key))

    assert not client.contains(key)


@pytest.mark.skipif(
    not sys.platform.startswith("linux"), reason="Reads memory use from `/proc`"
)
def test_delete_frees_the_deleted_value(client):
    # Dragon's `erase` is a pop: it returns the deleted value to the client,
    # which must free it. Deleting values must not grow the process by their
    # total size.
    key = "some-large-object-to-delete"
    value = os.urandom(256 * 1024)
    n_deletes = 256

    def put_and_delete(n):
        for _ in range(n):
            client.put_picklable(key, value)
            client.delete_item(OutgoingHandle(key))

    put_and_delete(16)  # Warm up the allocators.
    before = _anon_memory_bytes()
    put_and_delete(n_deletes)
    growth = _anon_memory_bytes() - before

    deleted = n_deletes * len(value)
    assert growth < deleted / 4, (
        f"Deleting {deleted / 2**20:.0f} MiB of values grew the process by "
        f"{growth / 2**20:.0f} MiB"
    )
