"""Serving side of the radex ORBIT plugin.

The plugin runs inside an ORBIT endpoint next to a radex store (Dragon DDict
or Redis).  A session attaches to one store with the native radex client and
performs the data calls that `radex.orbit.client.OrbitClient` sends over
ORBIT.  Store lifecycle is not handled here: stores are started by rhapsody
(locally, or remotely via rhapsody's ``OrbitDataBackend``).

The compiled radex core is imported only when a session attaches, so the
plugin module itself loads without it.

The native calls hold the GIL.  Waiting for a key is therefore done here, in
short native ``contains`` polls with ``asyncio.sleep`` in between, never with
the native ``wait_for_*`` (which would stall the endpoint, its transport
included, for the whole wait).  Attaching still blocks for up to the attach
timeout.
"""

import asyncio
import logging
import math
import os
import threading
import time

import numpy as np
from fastapi import FastAPI, HTTPException, Request
from radical.orbit.plugin_base import Plugin
from radical.orbit.plugin_session_base import PluginSession

from radex import exceptions as rx_exc
from radex.orbit.client import (
    ROUTE_ATTACH,
    ROUTE_CONTAINS,
    ROUTE_DELETE,
    ROUTE_GET_SCALAR,
    ROUTE_GET_TENSOR,
    ROUTE_PUT_SCALAR,
    ROUTE_PUT_TENSOR,
    SUPPORTED_DTYPES,
    OrbitClient,
    decode_scalar,
    decode_tensor,
    encode_scalar,
    encode_tensor,
)

log = logging.getLogger("radex.orbit")


# Seconds between key polls while waiting; same knob as the native clients
# (RADEX_POLL_INTERVAL, milliseconds).
def _poll_interval() -> float:
    try:
        ms = int(os.environ.get("RADEX_POLL_INTERVAL", "100"))
    except ValueError:
        log.warning("ignoring non-integer RADEX_POLL_INTERVAL")
        ms = 100
    return max(ms, 1) / 1000


_POLL_INTERVAL = _poll_interval()

# The native Redis client reads its target from the environment; serialize
# the set-env / construct / restore-env sequence across sessions.
_ENV_LOCK = threading.Lock()


def _native_client(kind: str, descriptor: str, timeout: int, opts: str):
    """Construct a native radex client for one store (blocking)."""
    if kind == "dragon":
        from radex.clients.core import DragonClient

        return DragonClient(descriptor=descriptor, timeout=timeout)

    if kind == "redis":
        from radex.clients.core import RedisClient

        with _ENV_LOCK:
            saved = {k: os.environ.get(k) for k in ("RADEX_STORE", "RADEX_STORE_OPTS")}
            os.environ["RADEX_STORE"] = descriptor
            os.environ["RADEX_STORE_OPTS"] = opts
            try:
                return RedisClient()
            finally:
                for k, v in saved.items():
                    if v is None:
                        os.environ.pop(k, None)
                    else:
                        os.environ[k] = v

    raise ValueError(f"unknown store kind {kind!r}; use 'dragon' or 'redis'")


def _handles():
    from radex.handles.handles import IncomingHandle, OutgoingHandle

    return IncomingHandle, OutgoingHandle


# radex error -> HTTP status; the client maps 404/408 back to radex errors.
_STATUS = (
    (rx_exc.KeyNotFoundError, 404, "key not found"),
    (rx_exc.TimeoutError, 408, "timeout"),
    (rx_exc.TypeMismatchError, 400, "type mismatch"),
    (rx_exc.BackendUnavailableError, 503, "backend unavailable"),
)


class RadexSession(PluginSession):
    """One client session, attached to at most one radex store."""

    def __init__(self, sid: str):
        super().__init__(sid)
        self._client = None
        self._kind = None

    async def attach(
        self, kind: str, descriptor: str, timeout: int = 5, opts: str = "Standalone"
    ) -> dict:
        self._check_active()
        try:
            self._client = await asyncio.to_thread(
                _native_client, kind, descriptor, timeout, opts
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except RuntimeError as e:  # RadexError, or a native connect failure
            raise HTTPException(
                status_code=503, detail=f"backend unavailable: attach failed: {e}"
            ) from e
        self._kind = kind
        return {"kind": kind}

    async def _call(self, method: str, *args):
        self._check_active()
        if self._client is None:
            raise HTTPException(
                status_code=409, detail="session is not attached to a store"
            )
        try:
            return await asyncio.to_thread(getattr(self._client, method), *args)
        except rx_exc.RadexError as e:
            for exc_type, status, label in _STATUS:
                if isinstance(e, exc_type):
                    raise HTTPException(
                        status_code=status, detail=f"{label}: {e}"
                    ) from e
            raise

    async def _await_key(self, key: str, timeout) -> None:
        """Return once `key` (data and metadata) is in the store; without a
        `timeout`, it must be there now."""
        keys = (key, f"metadata::{key}")
        deadline = None if timeout is None else time.monotonic() + float(timeout)
        while True:
            present = True
            for k in keys:
                present = present and bool(await self._call("contains", k))
            if present:
                return
            if deadline is None:
                raise HTTPException(status_code=404, detail=f"key not found: {key}")
            if time.monotonic() >= deadline:
                raise HTTPException(
                    status_code=408,
                    detail=f"timeout: {key} not in store after {timeout}s",
                )
            await asyncio.sleep(_POLL_INTERVAL)

    async def put_scalar(self, key: str, value, dtype: str) -> dict:
        if dtype not in SUPPORTED_DTYPES:
            raise HTTPException(status_code=400, detail=f"unsupported dtype {dtype!r}")
        try:
            scalar = decode_scalar(value, dtype)
        except (TypeError, ValueError, OverflowError) as e:
            raise HTTPException(status_code=400, detail=f"bad scalar: {e}") from e
        _, outgoing = _handles()
        await self._call("put_scalar", outgoing(key), scalar)
        return {}

    async def get_scalar(self, key: str, timeout=None) -> dict:
        await self._await_key(key, timeout)
        incoming, _ = _handles()
        value = np.asarray(await self._call("get_scalar", incoming(key)))
        return {"value": encode_scalar(value.item()), "dtype": value.dtype.name}

    async def put_tensor(self, key: str, payload: dict) -> dict:
        try:
            tensor = decode_tensor(payload)
        except (KeyError, TypeError, ValueError) as e:
            raise HTTPException(
                status_code=400, detail=f"bad tensor payload: {e}"
            ) from e
        if tensor.ndim == 0 or tensor.size == 0:
            raise HTTPException(status_code=400, detail="empty or 0-d tensor")
        _, outgoing = _handles()
        await self._call("put_tensor", outgoing(key), tensor)
        return {}

    async def get_tensor(self, key: str, timeout=None) -> dict:
        await self._await_key(key, timeout)
        incoming, _ = _handles()
        tensor = await self._call("get_tensor", incoming(key))
        try:
            return encode_tensor(np.asarray(tensor))
        except ValueError as e:
            raise HTTPException(status_code=413, detail=str(e)) from e

    async def contains(self, key: str) -> dict:
        return {"contains": bool(await self._call("contains", key))}

    async def delete_item(self, key: str) -> dict:
        _, outgoing = _handles()
        await self._call("delete_item", outgoing(key))
        return {}

    async def close(self) -> dict:
        self._client = None
        return await super().close()


class PluginRadex(Plugin):
    """radex data exchange over ORBIT.

    - POST /radex/attach/{sid}      - attach the session to a store
    - POST /radex/put_scalar/{sid}  - store a scalar
    - POST /radex/get_scalar/{sid}  - read (or wait for) a scalar
    - POST /radex/put_tensor/{sid}  - store a tensor
    - POST /radex/get_tensor/{sid}  - read (or wait for) a tensor
    - POST /radex/contains/{sid}    - check for a key
    - POST /radex/delete/{sid}      - delete a key
    """

    plugin_name = "radex"
    session_class = RadexSession
    client_class = OrbitClient
    version = "0.0.1"

    ui_config = {
        "icon": "🔀",
        "title": "radex",
        "description": "Exchange scalars and tensors with a radex store on this endpoint.",
    }

    @classmethod
    def is_enabled(cls, app: FastAPI) -> bool:
        """Load where the stores live: compute nodes and standalone hosts."""
        from radical.orbit.utils import host_role

        return host_role(app)["role"] in ("compute", "standalone")

    def __init__(self, app: FastAPI, instance_name: str = "radex"):
        super().__init__(app, instance_name)

        self.add_route_post(ROUTE_ATTACH, self.attach)
        self.add_route_post(ROUTE_PUT_SCALAR, self.put_scalar)
        self.add_route_post(ROUTE_GET_SCALAR, self.get_scalar)
        self.add_route_post(ROUTE_PUT_TENSOR, self.put_tensor)
        self.add_route_post(ROUTE_GET_TENSOR, self.get_tensor)
        self.add_route_post(ROUTE_CONTAINS, self.contains)
        self.add_route_post(ROUTE_DELETE, self.delete_item)

    @staticmethod
    def _timeout(data: dict, default=None):
        """A finite, non-negative number of seconds (or `default` if absent)."""
        timeout = data.get("timeout", default)
        if timeout is None:
            return None
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout < 0
        ):
            raise HTTPException(status_code=400, detail="bad timeout")
        return timeout

    @staticmethod
    async def _body(request: Request, *required: str) -> dict:
        data = await request.json()
        if not isinstance(data, dict):
            raise HTTPException(
                status_code=400, detail="request body must be an object"
            )
        missing = [k for k in required if k not in data]
        if missing:
            raise HTTPException(status_code=400, detail=f"missing fields: {missing}")
        return data

    async def attach(self, request: Request) -> dict:
        data = await self._body(request, "kind", "descriptor")
        timeout = self._timeout(data, default=5)
        if timeout is None:
            raise HTTPException(status_code=400, detail="bad timeout")
        return await self._forward(
            request.path_params["sid"],
            RadexSession.attach,
            kind=data["kind"],
            descriptor=data["descriptor"],
            timeout=math.ceil(timeout),
            opts=str(data.get("opts", "Standalone")),
        )

    async def put_scalar(self, request: Request) -> dict:
        data = await self._body(request, "key", "value", "dtype")
        return await self._forward(
            request.path_params["sid"],
            RadexSession.put_scalar,
            key=data["key"],
            value=data["value"],
            dtype=data["dtype"],
        )

    async def get_scalar(self, request: Request) -> dict:
        data = await self._body(request, "key")
        return await self._forward(
            request.path_params["sid"],
            RadexSession.get_scalar,
            key=data["key"],
            timeout=self._timeout(data),
        )

    async def put_tensor(self, request: Request) -> dict:
        data = await self._body(request, "key", "dtype", "shape", "data")
        return await self._forward(
            request.path_params["sid"],
            RadexSession.put_tensor,
            key=data["key"],
            payload=data,
        )

    async def get_tensor(self, request: Request) -> dict:
        data = await self._body(request, "key")
        return await self._forward(
            request.path_params["sid"],
            RadexSession.get_tensor,
            key=data["key"],
            timeout=self._timeout(data),
        )

    async def contains(self, request: Request) -> dict:
        data = await self._body(request, "key")
        return await self._forward(
            request.path_params["sid"], RadexSession.contains, key=data["key"]
        )

    async def delete_item(self, request: Request) -> dict:
        data = await self._body(request, "key")
        return await self._forward(
            request.path_params["sid"], RadexSession.delete_item, key=data["key"]
        )
