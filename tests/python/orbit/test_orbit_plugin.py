"""Tests for the radex ORBIT plugin and client.

The compiled radex core is replaced by an in-memory fake, so these tests need
``radical.orbit``, ``fastapi`` and ``numpy`` but no C++ build.
"""

import os
from unittest.mock import patch

import numpy as np
import pytest

pytest.importorskip("radical.orbit")

from fastapi import FastAPI  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402

from radex import exceptions as rx_exc  # noqa: E402
from radex.orbit import plugin as plugin_mod  # noqa: E402
from radex.orbit.client import TENSOR_BYTES_LIMIT  # noqa: E402
from radex.orbit.client import OrbitClient  # noqa: E402
from radex.orbit.client import decode_tensor  # noqa: E402
from radex.orbit.client import encode_tensor  # noqa: E402
from radex.orbit.plugin import PluginRadex  # noqa: E402


class _Handle:
    def __init__(self, key):
        self.key = key


class _FakeNativeClient:
    """In-memory stand-in for radex.clients.core.{Dragon,Redis}Client."""

    def __init__(self):
        self.store = {}

    def contains(self, key):
        return key in self.store

    def put_scalar(self, handle, value):
        self.store[handle.key] = value
        self.store[f"metadata::{handle.key}"] = "scalar"

    def get_scalar(self, handle):
        if self.store.get(f"metadata::{handle.key}") != "scalar":
            raise rx_exc.RankMismatchError(f"{handle.key} is not a scalar")
        return self.store[handle.key]

    def put_tensor(self, handle, tensor):
        self.store[handle.key] = tensor
        self.store[f"metadata::{handle.key}"] = "tensor"

    def get_tensor(self, handle):
        return self.store[handle.key]

    def wait_for_scalar(self, handle, timeout):
        raise AssertionError("native waits hold the GIL; the plugin must poll")

    wait_for_tensor = wait_for_scalar

    def delete_item(self, handle):
        self.store.pop(handle.key, None)
        self.store.pop(f"metadata::{handle.key}", None)


@pytest.fixture
def native():
    client = _FakeNativeClient()
    calls = []

    def _factory(kind, descriptor, timeout, opts):
        if kind not in ("dragon", "redis"):
            raise ValueError(f"unknown store kind {kind!r}")
        if descriptor == "unreachable:1":
            raise RuntimeError("connect failed")
        calls.append((kind, descriptor, timeout, opts))
        return client

    with (
        patch.object(plugin_mod, "_native_client", side_effect=_factory),
        patch.object(plugin_mod, "_handles", return_value=(_Handle, _Handle)),
    ):
        client.calls = calls
        yield client


@pytest.fixture
def http():
    app = FastAPI()
    plugin = PluginRadex(app)
    return plugin, TestClient(app)


def _session(plugin, http_client):
    resp = http_client.post(f"{plugin.namespace}/register_session")
    assert resp.status_code == 200
    return resp.json()["sid"]


@pytest.fixture
def rx(http, native):
    """An OrbitClient attached to the fake store, talking plain HTTP."""
    plugin, http_client = http
    client = OrbitClient.__new__(OrbitClient)
    client._sid = _session(plugin, http_client)
    client._url = lambda path: f"{plugin.namespace}/{path}"
    client._request = lambda method, url, **kw: http_client.request(method, url, **kw)
    client._raise = _raise
    client.attach("redis", "node1:6379", timeout=2.5)
    return client


def _raise(resp, context=""):
    if resp.status_code >= 400:
        raise RuntimeError(f"{resp.status_code}: {resp.json().get('detail')}")


def test_tensor_codec_roundtrip():
    for dtype in ("int32", "int64", "float32", "float64"):
        array = np.arange(12, dtype=dtype).reshape(3, 4)
        out = decode_tensor(encode_tensor(array))
        assert out.dtype == array.dtype
        np.testing.assert_array_equal(out, array)


def test_tensor_codec_rejects_dtype_and_size():
    with pytest.raises(TypeError):
        encode_tensor(np.zeros(3, dtype=np.complex64))
    with pytest.raises(ValueError, match="transfer limit"):
        encode_tensor(np.zeros(TENSOR_BYTES_LIMIT // 8 + 1, dtype=np.float64))


def test_attach(rx, native):
    assert native.calls == [("redis", "node1:6379", 3, "Standalone")]


def test_attach_unknown_kind(http, native):
    plugin, http_client = http
    sid = _session(plugin, http_client)
    resp = http_client.post(
        f"{plugin.namespace}/attach/{sid}", json={"kind": "s3", "descriptor": "x"}
    )
    assert resp.status_code == 400


def test_calls_before_attach(http, native):
    plugin, http_client = http
    sid = _session(plugin, http_client)
    resp = http_client.post(f"{plugin.namespace}/contains/{sid}", json={"key": "a"})
    assert resp.status_code == 409


def test_scalar_roundtrip(rx, native):
    rx.put_scalar("step", 42)
    rx.put_scalar("loss", 0.25)
    assert native.store["step"] == 42 and native.store["step"].dtype == np.int64
    assert rx.get_scalar("step") == 42
    assert rx.get_scalar("loss") == 0.25
    assert rx.get_scalar("loss", timeout=1).dtype == np.float64


def test_scalar_numpy_dtype_kept(rx, native):
    rx.put_scalar("x", np.float32(1.5))
    assert native.store["x"].dtype == np.float32
    assert rx.get_scalar("x").dtype == np.float32


def test_tensor_roundtrip(rx):
    array = np.linspace(0, 1, 16, dtype=np.float32).reshape(4, 4)
    rx.put_tensor("w", array)
    out = rx.get_tensor("w")
    assert out.dtype == np.float32
    np.testing.assert_array_equal(out, array)


def test_contains_and_delete(rx):
    assert rx.contains("k") is False
    rx.put_scalar("k", 1)
    assert rx.contains("k") is True
    rx.delete_item("k")
    assert rx.contains("k") is False


def test_missing_key_maps_to_radex_errors(rx):
    with pytest.raises(rx_exc.KeyNotFoundError):
        rx.get_scalar("nope")
    with pytest.raises(rx_exc.TimeoutError):
        rx.get_tensor("nope", timeout=0.1)


def test_put_scalar_bad_dtype(http, rx):
    plugin, http_client = http
    resp = http_client.post(
        f"{plugin.namespace}/put_scalar/{rx.sid}",
        json={"key": "a", "value": 1, "dtype": "complex64"},
    )
    assert resp.status_code == 400


def test_missing_fields(http, rx):
    plugin, http_client = http
    resp = http_client.post(
        f"{plugin.namespace}/put_tensor/{rx.sid}", json={"key": "a"}
    )
    assert resp.status_code == 400


def test_consumer_import_registers_plugin():
    from radical.orbit.plugin_base import Plugin

    import radex.orbit  # noqa: F401

    assert Plugin.get_plugin_class("radex").client_class is OrbitClient


def test_enabled_on_compute_and_standalone_only():
    app = FastAPI()
    for role, enabled in (
        ("compute", True),
        ("standalone", True),
        ("broker", False),
        ("login", False),
    ):
        with patch("radical.orbit.utils.host_role", return_value={"role": role}):
            assert PluginRadex.is_enabled(app) is enabled


def test_tensor_codec_big_endian():
    array = np.arange(6, dtype=">f8").reshape(2, 3)
    out = decode_tensor(encode_tensor(array))
    np.testing.assert_array_equal(out, array)


def test_tensor_codec_rejects_empty_and_0d():
    with pytest.raises(ValueError):
        encode_tensor(np.zeros((0, 3)))
    with pytest.raises(ValueError):
        encode_tensor(np.array(1.0))


def test_non_finite_scalars(rx):
    for value in (float("nan"), float("inf"), float("-inf")):
        rx.put_scalar("x", value)
        out = rx.get_scalar("x")
        assert out.dtype == np.float64
        assert (np.isnan(out) and np.isnan(value)) or out == value


def test_put_scalar_rejects_non_numeric(rx):
    with pytest.raises(TypeError):
        rx.put_scalar("x", "abc")


def test_wait_polls_until_key_appears(rx, native):
    import threading

    timer = threading.Timer(0.3, native.put_scalar, (_Handle("late"), 7))
    timer.start()
    try:
        assert rx.get_scalar("late", timeout=5) == 7
    finally:
        timer.cancel()


def test_type_mismatch_maps_to_radex_error(rx):
    rx.put_tensor("t", np.ones(3))
    with pytest.raises(rx_exc.TypeMismatchError):
        rx.get_scalar("t")


def test_attach_connect_failure_is_backend_unavailable(rx):
    with pytest.raises(rx_exc.BackendUnavailableError):
        rx.attach("redis", "unreachable:1")


def test_attach_bad_timeout(http, native):
    plugin, http_client = http
    sid = _session(plugin, http_client)
    url = f"{plugin.namespace}/attach/{sid}"
    for timeout in (None, -1, "5", True):
        resp = http_client.post(
            url, json={"kind": "redis", "descriptor": "x", "timeout": timeout}
        )
        assert resp.status_code == 400, timeout


def test_put_tensor_server_rejects_bad_payloads(http, rx):
    plugin, http_client = http
    url = f"{plugin.namespace}/put_tensor/{rx.sid}"
    bad_dtype = {"key": "a", "dtype": "uint8", "shape": [1], "data": "AA=="}
    empty = {"key": "a", "dtype": "float64", "shape": [0], "data": ""}
    assert http_client.post(url, json=bad_dtype).status_code == 400
    assert http_client.post(url, json=empty).status_code == 400


def test_redis_client_env_is_set_and_restored(monkeypatch):
    import sys
    import types

    seen = {}

    class _RedisClient:
        def __init__(self):
            seen["store"] = os.environ.get("RADEX_STORE")
            seen["opts"] = os.environ.get("RADEX_STORE_OPTS")

    core = types.ModuleType("radex.clients.core")
    core.RedisClient = _RedisClient
    monkeypatch.setitem(sys.modules, "radex.clients.core", core)
    monkeypatch.setenv("RADEX_STORE", "previous")
    monkeypatch.delenv("RADEX_STORE_OPTS", raising=False)

    plugin_mod._native_client("redis", "node1:6379", 5, "Standalone")

    assert seen == {"store": "node1:6379", "opts": "Standalone"}
    assert os.environ["RADEX_STORE"] == "previous"
    assert "RADEX_STORE_OPTS" not in os.environ


def test_get_rejects_non_finite_timeout(http, rx):
    plugin, http_client = http
    url = f"{plugin.namespace}/get_scalar/{rx.sid}"
    for timeout in (-1, "5", True):
        resp = http_client.post(url, json={"key": "a", "timeout": timeout})
        assert resp.status_code == 400, timeout
    # NaN / Infinity only arrive in hand-made bodies (JSON extension tokens)
    for token in ("NaN", "Infinity"):
        resp = http_client.post(
            url,
            content=f'{{"key": "a", "timeout": {token}}}',
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 400, token


def test_poll_interval_parsing(monkeypatch):
    monkeypatch.setenv("RADEX_POLL_INTERVAL", "abc")
    assert plugin_mod._poll_interval() == 0.1
    monkeypatch.setenv("RADEX_POLL_INTERVAL", "0")
    assert plugin_mod._poll_interval() == 0.001
