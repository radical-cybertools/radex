"""Client side of the radex ORBIT plugin.

`OrbitClient` exposes the radex client API (``put_scalar``, ``get_tensor``,
...) over ORBIT: every call travels to the endpoint hosting the store, where
the plugin performs it with the native radex client.  This module is pure
Python -- it needs ``radical.orbit`` and ``numpy``, but not the compiled radex
core -- so a consumer that is not on the HPC resource (e.g. a digital twin on
the broker host) can exchange data without a C++ build.

Keys are plain strings: they name the same item a native client reaches with
``OutgoingHandle(key)`` / ``IncomingHandle(key)``.

Tensors travel as raw bytes and are bounded by the default ORBIT frame cap;
larger ones are rejected before they are sent.  A deployment that tunes the
frame cap below its default sees a transport error instead.
"""

import base64
import math
from typing import Optional

import numpy as np
from radical.orbit.client import PluginClient
from radical.orbit.protocol import FRAME_CAP

from radex.exceptions import BackendUnavailableError, KeyNotFoundError
from radex.exceptions import TimeoutError as RadexTimeoutError
from radex.exceptions import TypeMismatchError

ROUTE_ATTACH = "attach/{sid}"
ROUTE_PUT_SCALAR = "put_scalar/{sid}"
ROUTE_GET_SCALAR = "get_scalar/{sid}"
ROUTE_PUT_TENSOR = "put_tensor/{sid}"
ROUTE_GET_TENSOR = "get_tensor/{sid}"
ROUTE_CONTAINS = "contains/{sid}"
ROUTE_DELETE = "delete/{sid}"

SUPPORTED_DTYPES = ("int32", "int64", "float32", "float64")

# Raw tensor bytes per request.  Base64 inflates by 4/3, so half the frame cap
# leaves room for the encoding and the envelope.
TENSOR_BYTES_LIMIT = FRAME_CAP // 2


def encode_tensor(tensor: np.ndarray) -> dict:
    """Encode an array as ``{dtype, shape, data}`` (C order, native byte
    order, base64)."""
    dtype = tensor.dtype.name
    if dtype not in SUPPORTED_DTYPES:
        raise TypeError(
            f"unsupported tensor dtype {dtype!r}; use one of {SUPPORTED_DTYPES}"
        )
    if tensor.ndim == 0 or tensor.size == 0:
        raise ValueError("tensors must have at least one dimension and element")
    raw = np.ascontiguousarray(tensor, dtype=tensor.dtype.newbyteorder("=")).tobytes()
    if len(raw) > TENSOR_BYTES_LIMIT:
        raise ValueError(
            f"tensor of {len(raw)} bytes exceeds the ORBIT transfer limit "
            f"of {TENSOR_BYTES_LIMIT} bytes"
        )
    return {
        "dtype": dtype,
        "shape": list(tensor.shape),
        "data": base64.b64encode(raw).decode("ascii"),
    }


def decode_tensor(payload: dict) -> np.ndarray:
    """Inverse of `encode_tensor`."""
    if payload["dtype"] not in SUPPORTED_DTYPES:
        raise TypeError(f"unsupported tensor dtype {payload['dtype']!r}")
    raw = base64.b64decode(payload["data"])
    array = np.frombuffer(raw, dtype=np.dtype(payload["dtype"]))
    return array.reshape(payload["shape"]).copy()


def encode_scalar(value):
    """JSON-safe form of a scalar: non-finite floats travel as strings
    (``"nan"``, ``"inf"``, ``"-inf"``), which JSON cannot carry."""
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    return value


def decode_scalar(value, dtype: str):
    """Inverse of `encode_scalar`, typed as `dtype`."""
    return np.dtype(dtype).type(float(value) if isinstance(value, str) else value)


class OrbitClient(PluginClient):
    """radex data access over ORBIT.

    Obtain one via ``runtime.get_plugin(endpoint, 'radex')``, then `attach` it
    to a store the endpoint can reach (typically one started there through
    rhapsody's ``OrbitDataBackend``)::

        rx = runtime.get_plugin("endpoint_1", "radex")
        rx.attach("redis", descriptor)        # descriptor: Endpoint.serialize()
        rx.put_scalar("step", 42)
        rx.get_tensor("weights", timeout=10)
    """

    def attach(
        self, kind: str, descriptor: str, timeout: int = 5, opts: str = "Standalone"
    ) -> dict:
        """Attach this session to a store.

        Args:
            kind: Store type, ``"dragon"`` or ``"redis"``.
            descriptor: The store's serialized endpoint as seen on the
                endpoint host (DDict descriptor, or ``host:port``).
            timeout: Seconds the endpoint may take to attach.  The endpoint
                is blocked meanwhile; keep it short.
            opts: Redis only: the store options (``RADEX_STORE_OPTS``),
                e.g. ``"Standalone"``.
        """
        body = {"kind": kind, "descriptor": descriptor, "timeout": timeout}
        return self._post(ROUTE_ATTACH, {**body, "opts": opts})

    def put_scalar(self, key: str, value) -> None:
        """Store an int or float scalar; numpy scalars keep their dtype,
        Python ints and floats become int64 and float64."""
        scalar = np.asarray(value)
        if scalar.ndim != 0 or scalar.dtype.kind not in "iuf":
            raise TypeError(f"not an int or float scalar: {value!r}")
        dtype = scalar.dtype.name
        if dtype not in SUPPORTED_DTYPES:
            dtype = "float64" if scalar.dtype.kind == "f" else "int64"
        # .item(): numpy scalars are not JSON-serializable; dtype travels apart
        body = {"key": key, "value": encode_scalar(scalar.item()), "dtype": dtype}
        self._post(ROUTE_PUT_SCALAR, body)

    def get_scalar(self, key: str, timeout: Optional[float] = None):
        """Read a scalar; with `timeout`, wait up to that many seconds for it
        (keep it below the ORBIT call timeout, 600 s by default)."""
        reply = self._post(ROUTE_GET_SCALAR, {"key": key, "timeout": timeout})
        return decode_scalar(reply["value"], reply["dtype"])

    def put_tensor(self, key: str, tensor: np.ndarray) -> None:
        """Store an n-dimensional array (int32/int64/float32/float64)."""
        self._post(ROUTE_PUT_TENSOR, {"key": key, **encode_tensor(tensor)})

    def get_tensor(self, key: str, timeout: Optional[float] = None) -> np.ndarray:
        """Read an array; with `timeout`, wait up to that many seconds for it
        (keep it below the ORBIT call timeout, 600 s by default)."""
        return decode_tensor(
            self._post(ROUTE_GET_TENSOR, {"key": key, "timeout": timeout})
        )

    def contains(self, key: str) -> bool:
        """Check whether `key` is present in the store."""
        return bool(self._post(ROUTE_CONTAINS, {"key": key})["contains"])

    def delete_item(self, key: str) -> None:
        """Delete `key` from the store."""
        self._post(ROUTE_DELETE, {"key": key})

    def _post(self, route: str, body: dict) -> dict:
        self._require_session()
        resp = self._request("POST", self._url(route.format(sid=self.sid)), json=body)
        detail = _detail(resp)
        for status, prefix, exc_type in _ERRORS:
            if resp.status_code == status and detail.startswith(prefix):
                raise exc_type(detail)
        self._raise(resp)
        return resp.json()


# (HTTP status, detail prefix) the plugin uses for radex errors -> radex error
_ERRORS = (
    (404, "key not found", KeyNotFoundError),
    (408, "timeout", RadexTimeoutError),
    (400, "type mismatch", TypeMismatchError),
    (503, "backend unavailable", BackendUnavailableError),
)


def _detail(resp) -> str:
    try:
        return str(resp.json().get("detail", ""))
    except Exception:
        return ""
