import math
import os
import time

import numpy as np
import pytest
import radex

_TRIVIAL_WAIT_TIME_LIMIT = 0.1  # seconds


def test_put_and_get_scalar(client, np_dtype, random_np_value):
    key = "some-value"
    assert not client.contains(key)

    client.put_scalar(key, random_np_value)
    assert client.contains(key)

    ret_val = client.get_scalar(key)
    assert random_np_value.dtype == ret_val.dtype == np_dtype
    assert random_np_value == ret_val


def test_put_and_trivial_wait_for_scalar(client, np_dtype, random_np_value):
    key = "some-value"
    assert not client.contains(key)

    client.put_scalar(key, random_np_value)
    assert client.contains(key)

    start_t = time.perf_counter()
    ret_val = client.wait_for_scalar(key, timeout=10)
    end_t = time.perf_counter()
    assert end_t - start_t < _TRIVIAL_WAIT_TIME_LIMIT
    assert random_np_value.dtype == ret_val.dtype == np_dtype
    assert random_np_value == ret_val


def test_put_and_wait_for_value(ddict, client, np_dtype, random_np_value):
    process = pytest.importorskip("dragon.native.process")

    key = "some-value"
    delay = 2  # seconds
    assert not client.contains(key)

    def put_key_after(dd, key, value, delay):
        start_t = time.perf_counter()
        client = radex.DragonClient(descriptor=dd, timeout=1)
        time.sleep(max(delay - (time.perf_counter() - start_t), 0))
        client.put_scalar(key, value)

    proc = process.Process(
        target=put_key_after, args=(ddict.serialize(), key, random_np_value, delay)
    )
    proc.start()
    start_t = time.perf_counter()
    try:
        ret_val = client.wait_for_scalar(key, timeout=10)
    finally:
        end_t = time.perf_counter()
        proc.join()

    # Check that the read actually was delayed within a poll rate and a trivial
    # amount of time for process construction overhead. We can make this more
    # strict as we design a better "wait for key" implementation.
    # FIXME: We should expose the poll rate through the `radex` namespace rather
    #        than looking for magic env vars in the tests
    min_allowed_delay = delay
    max_allowed_delay = (
        delay + os.environ.get("RADEX_POLL_INTERVAL", 1) + _TRIVIAL_WAIT_TIME_LIMIT
    )
    assert min_allowed_delay < end_t - start_t < max_allowed_delay

    # Check correctness
    assert random_np_value.dtype == ret_val.dtype == np_dtype
    assert random_np_value == ret_val


def test_put_and_get_tensor(client, random_np_tensor, np_dtype):
    key = "some-tensor"
    assert not client.contains(key)

    client.put_tensor(key, random_np_tensor)
    assert client.contains(key)
    ret_tensor = client.get_tensor(key)

    assert random_np_tensor.dtype == ret_tensor.dtype == np_dtype
    assert random_np_tensor.shape == ret_tensor.shape
    assert (random_np_tensor == ret_tensor).all()


def test_put_and_trivial_wait_for_tensor(client, np_dtype, random_np_tensor):
    key = "some-tensor"
    assert not client.contains(key)

    client.put_tensor(key, random_np_tensor)
    assert client.contains(key)

    start_t = time.perf_counter()
    ret_val = client.wait_for_tensor(key, timeout=10)
    end_t = time.perf_counter()
    assert end_t - start_t < _TRIVIAL_WAIT_TIME_LIMIT
    assert random_np_tensor.dtype == ret_val.dtype == np_dtype
    assert (random_np_tensor == ret_val).all()


def test_put_and_wait_for_tensor(ddict, client, np_dtype, random_np_tensor):
    process = pytest.importorskip("dragon.native.process")

    key = "some-value"
    delay = 1  # seconds
    assert not client.contains(key)

    def put_key_after(dd, key, value, delay):
        start_t = time.perf_counter()
        client = radex.DragonClient(descriptor=dd, timeout=1)
        time.sleep(max(delay - (time.perf_counter() - start_t), 0))
        client.put_tensor(key, value)

    proc = process.Process(
        target=put_key_after, args=(ddict.serialize(), key, random_np_tensor, delay)
    )
    proc.start()
    start_t = time.perf_counter()
    try:
        ret_val = client.wait_for_tensor(key, timeout=10)
    finally:
        end_t = time.perf_counter()
        proc.join()

    # Check that the read actually was delayed within a poll rate and a trivial
    # amount of time for process construction overhead. We can make this more
    # strict as we design a better "wait for key" implementation.
    # FIXME: We should expose the poll rate through the `radex` namespace rather
    #        than looking for magic env vars in the tests
    min_allowed_delay = delay
    max_allowed_delay = (
        delay + os.environ.get("RADEX_POLL_INTERVAL", 1) + _TRIVIAL_WAIT_TIME_LIMIT
    )
    assert min_allowed_delay < end_t - start_t < max_allowed_delay

    # Check correctness
    assert random_np_tensor.dtype == ret_val.dtype == np_dtype
    assert (random_np_tensor == ret_val).all()


@pytest.mark.parametrize("size", [pytest.param(int(1e6), id="size=1MB")])
@pytest.mark.parametrize(
    "n_dims", [pytest.param(n, id=f"shape={n}D") for n in range(1, 5)]
)
def test_put_and_get_tensor_of_size(client, np_dtype, size, n_dims):
    min_n_elements = math.ceil(size / np.dtype(np_dtype).itemsize)
    n_elements_per_dim = math.ceil(math.pow(min_n_elements, 1 / n_dims))
    shape = tuple([n_elements_per_dim] * n_dims)
    n_elements = math.prod(shape)
    assert n_elements >= min_n_elements, f"Tensor is smaller than {size} bytes"
    assert len(shape) == n_dims, f"Got {len(shape)} dims but expected {n_dims}"

    key = "spam-eggs"
    tensor = np.arange(n_elements, dtype=np_dtype).reshape(shape)

    client.put_tensor(key, tensor)
    assert client.contains(key)
    ret_tensor = client.get_tensor(key)

    assert tensor.dtype == ret_tensor.dtype == np_dtype
    assert tensor.shape == ret_tensor.shape == shape
    assert (tensor == ret_tensor).all()


@pytest.mark.parametrize(
    "value, expected_dtype",
    [
        pytest.param(value, dtype, id=f"{value=}-dtype={dtype.__name__}")
        for value, dtype in [
            (-123, np.int32),
            (0, np.int32),
            (123, np.int32),
            (-10.0, np.float64),
            (-22.5, np.float64),
            (0.0, np.float64),
            (0.75, np.float64),
        ]
    ],
)
def test_put_and_get_native_py_scalars(client, value, expected_dtype):
    key = "some-value"
    client.put_scalar(key, value)
    ret = client.get_scalar(key)
    assert ret.dtype == expected_dtype
    assert ret == value


def test_put_and_get_pickleable(client, random_picklable):
    key = "some-obj"
    assert not client.contains(key)
    client.put_picklable(key, random_picklable)
    assert client.contains(key)

    ret_val = client.get_picklable(key)
    assert type(random_picklable) == type(ret_val)
    assert random_picklable == ret_val


def test_put_and_trivial_wait_for_picklable(client, random_picklable):
    key = "some-obj"
    assert not client.contains(key)

    client.put_picklable(key, random_picklable)
    assert client.contains(key)

    start_t = time.perf_counter()
    ret_val = client.wait_for_picklable(key, timeout=10)
    end_t = time.perf_counter()
    assert end_t - start_t < _TRIVIAL_WAIT_TIME_LIMIT
    assert type(random_picklable) == type(ret_val)
    assert random_picklable == ret_val


def test_put_and_wait_for_picklable(ddict, client, random_picklable):
    process = pytest.importorskip("dragon.native.process")

    key = "some-obj"
    delay = 2  # seconds
    assert not client.contains(key)

    def put_key_after(dd, key, value, delay):
        start_t = time.perf_counter()
        client = radex.DragonClient(descriptor=dd, timeout=1)
        time.sleep(max(delay - (time.perf_counter() - start_t), 0))
        client.put_picklable(key, value)

    proc = process.Process(
        target=put_key_after, args=(ddict.serialize(), key, random_picklable, delay)
    )
    proc.start()
    start_t = time.perf_counter()
    try:
        ret_val = client.wait_for_picklable(key, timeout=10)
    finally:
        end_t = time.perf_counter()
        proc.join()

    # Check that the read actually was delayed within a poll rate and a trivial
    # amount of time for process construction overhead. We can make this more
    # strict as we design a better "wait for key" implementation.
    # FIXME: We should expose the poll rate through the `radex` namespace rather
    #        than looking for magic env vars in the tests
    min_allowed_delay = delay
    max_allowed_delay = (
        delay + os.environ.get("RADEX_POLL_INTERVAL", 1) + _TRIVIAL_WAIT_TIME_LIMIT
    )
    assert min_allowed_delay < end_t - start_t < max_allowed_delay

    # Check correctness
    assert type(random_picklable) == type(ret_val)
    assert random_picklable == ret_val
