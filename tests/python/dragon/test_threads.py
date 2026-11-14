"""The Dragon client's thread contract, as `radex/dragon.hpp` states it.

A client runs one call at a time, whichever threads make the calls; calls on
different clients run at once. A call that fails, as a timeout does, raises a
RaDex error and leaves its client, and the thread that made it, able to make
every later call.

Dragon 0.15.0 keys each dictionary request by a descriptor that its C++ API
leaves uninitialized, so before RaDex gave each request its own key, a request
that failed stayed in Dragon's request map and failed every later call that
reused its key: the same call from the same thread, on any client.
"""

import threading
import uuid

import pytest

import radex.exceptions
from radex.clients.core import DragonClient
from radex.handles.handles import OutgoingHandle

# A delete of a missing key waits for the client's timeout, then fails: the
# cheapest way to make a call fail after Dragon has created its request.
SHORT_TIMEOUT = 1
ROUNDS = 200
THREADS = 8


def _fail_one_call(client):
    with pytest.raises(RuntimeError):
        client.delete_item(OutgoingHandle(f"missing-{uuid.uuid4()}"))


def _round_trip(client, key, value):
    """Every call the clients make, once, checking each result."""
    client.put_picklable(key, value)
    assert client.contains(key)
    assert client.get_picklable(key) == value
    client.put_picklable(key, value + b"!")
    assert client.get_picklable(key) == value + b"!"
    client.delete_item(OutgoingHandle(key))
    assert not client.contains(key)
    with pytest.raises(radex.exceptions.KeyNotFoundError):
        client.get_picklable(key)


def _run_threads(target, n):
    errors = []

    def wrapped(i):
        try:
            target(i)
        except BaseException as exc:  # pytest.fail raises a BaseException
            errors.append(f"thread {i}: {type(exc).__name__}: {exc}")

    threads = [threading.Thread(target=wrapped, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return errors


def test_a_timed_out_call_raises_a_radex_timeout(ddict):
    client = DragonClient(descriptor=ddict.serialize(), timeout=SHORT_TIMEOUT)
    with pytest.raises(radex.exceptions.TimeoutError, match="DRAGON_TIMEOUT"):
        client.delete_item(OutgoingHandle(f"missing-{uuid.uuid4()}"))


def test_every_call_works_after_a_failed_call(ddict):
    client = DragonClient(descriptor=ddict.serialize(), timeout=SHORT_TIMEOUT)
    _round_trip(client, "before", b"value")
    _fail_one_call(client)
    for i in range(3):
        _round_trip(client, f"after-{i}", b"value")


def test_a_new_client_in_the_same_thread_works_after_a_failed_call(ddict):
    client = DragonClient(descriptor=ddict.serialize(), timeout=SHORT_TIMEOUT)
    _fail_one_call(client)
    other = DragonClient(descriptor=ddict.serialize(), timeout=SHORT_TIMEOUT)
    for i in range(3):
        _round_trip(other, f"other-{i}", b"value")


def test_threads_with_their_own_clients_after_failed_calls(ddict):
    descriptor = ddict.serialize()

    def work(i):
        client = DragonClient(descriptor=descriptor, timeout=SHORT_TIMEOUT)
        _fail_one_call(client)
        for r in range(ROUNDS):
            _round_trip(client, f"own-{i}-{r}", f"{i}-{r}".encode())

    assert _run_threads(work, THREADS) == []


def test_threads_sharing_one_client(ddict):
    client = DragonClient(descriptor=ddict.serialize(), timeout=5)

    def work(i):
        for r in range(ROUNDS):
            _round_trip(client, f"shared-{i}-{r}", f"{i}-{r}".encode() * 100)

    assert _run_threads(work, THREADS) == []
