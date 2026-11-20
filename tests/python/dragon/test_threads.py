"""The Dragon client's thread contract, as `radex/dragon.hpp` states it.

A client runs one call at a time, whichever threads make the calls; calls on
different clients run at once. The calls that move bytes release the GIL, so
a thread waiting on Dragon does not stop the other threads.

No test here makes a call fail. With Dragon 0.15.0, a request that fails
stays in Dragon's request map, and later calls from the same thread, or from
a thread that reuses its stack, can fail with it.
"""

import threading
import time

import pytest

import radex.exceptions
from radex.clients.core import DragonClient
from radex.handles.handles import OutgoingHandle

TIMEOUT = 5
ROUNDS = 200
THREADS = 8


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


def test_threads_sharing_one_client(ddict):
    client = DragonClient(descriptor=ddict.serialize(), timeout=TIMEOUT)

    def work(i):
        for r in range(ROUNDS):
            _round_trip(client, f"shared-{i}-{r}", f"{i}-{r}".encode() * 100)

    assert _run_threads(work, THREADS) == []


def test_threads_with_their_own_clients(ddict):
    descriptor = ddict.serialize()

    def work(i):
        client = DragonClient(descriptor=descriptor, timeout=TIMEOUT)
        for r in range(ROUNDS):
            _round_trip(client, f"own-{i}-{r}", f"{i}-{r}".encode() * 100)

    assert _run_threads(work, THREADS) == []


def test_a_waiting_call_lets_other_threads_run(ddict):
    descriptor = ddict.serialize()
    waiter = DragonClient(descriptor=descriptor, timeout=TIMEOUT)
    writer = DragonClient(descriptor=descriptor, timeout=TIMEOUT)
    got = []

    def wait():
        got.append(waiter.wait_for_picklable("late", TIMEOUT))

    start = time.perf_counter()
    thread = threading.Thread(target=wait)
    thread.start()
    time.sleep(0.5)  # the waiter is now blocked in Dragon, waiting for "late"
    writer.put_picklable("late", b"value")
    thread.join(TIMEOUT)
    # Holding the GIL, the waiter would stop this thread until its wait timed
    # out, and the value would come too late.
    assert time.perf_counter() - start < TIMEOUT / 2
    assert got == [b"value"]
