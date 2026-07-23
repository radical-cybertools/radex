import dataclasses
import math

import numpy as np
import pytest


def test_put_and_get_scalar(client, np_dtype):
    rng = np.random.default_rng()
    if np.issubdtype(np_dtype, np.integer):
        value = rng.integers(0, 100, dtype=np_dtype)
    else:
        value = np_dtype(rng.random(dtype=np_dtype))

    key = "some-value"
    assert not client.contains(key)

    client.put_scalar(key, value)
    assert client.contains(key)

    ret_val = client.get_scalar(key)
    assert value.dtype == ret_val.dtype == np_dtype
    assert value == ret_val


@pytest.mark.parametrize(
    "size, shape",
    [
        pytest.param(size, shape, id=f"{size=}-{shape=}")
        for size, shape in [
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
def test_put_and_get_tensor(client, size, shape, np_dtype):
    key = "some-tensor"
    tensor = np.arange(size, dtype=np_dtype).reshape(shape)

    assert not client.contains(key)
    client.put_tensor(key, tensor)
    assert client.contains(key)
    ret_tensor = client.get_tensor(key)

    assert tensor.dtype == ret_tensor.dtype == np_dtype
    assert tensor.shape == ret_tensor.shape == shape
    assert (tensor == ret_tensor).all()


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


@dataclasses.dataclass(frozen=True)
class MyPickleable:
    some_str: str
    some_int: int


@pytest.mark.parametrize(
    "obj",
    [
        pytest.param(obj, id=str(obj))
        for obj in [
            MyPickleable("spam", 123),
            MyPickleable("eggs", 0),
            MyPickleable("ham", -72),
        ]
    ],
)
def test_put_and_get_pickleable(client, obj):
    key = "some-obj"
    assert not client.contains(key)
    client.put_picklable(key, obj)
    assert client.contains(key)
