from __future__ import annotations

import abc
import asyncio
import enum


class StoreState(enum.Enum):
    CREATED = "CREATED"
    STARTING = "STARTING"
    READY = "READY"
    FAILED = "FAILED"
    SHUTDOWN = "SHUTDOWN"


_TERMINAL_STATES = frozenset({StoreState.FAILED, StoreState.SHUTDOWN})


class StoreError(Exception):
    """Base class for all radex.store errors."""


class StoreStartupError(StoreError):
    """Raised when a Store fails to reach READY during start()."""


class StoreStateError(StoreError):
    """Raised when a Store method is invoked in an invalid lifecycle state."""


class StoreNotReadyError(StoreStateError):
    """Raised by `.endpoints` before a successful start()."""


class StoreTerminatedError(StoreStateError):
    """Raised by start() on a Store that is already FAILED or SHUTDOWN."""


class Endpoint(abc.ABC):
    """Backend-specific connection information for one Store instance/node.

    Deliberately generic: a Redis node has a host/port, a Dragon DDict has an
    opaque serialized descriptor, and neither concept is assumed by callers
    that only depend on this interface.
    """

    @abc.abstractmethod
    def serialize(self) -> str:
        """Return a string a caller can pass through explicitly (env var,
        kwarg, task arg) to reconnect a client elsewhere. Store never sets
        this into os.environ itself -- callers own that decision."""


class Store(abc.ABC):
    """Backend-independent lifecycle for a RADEX data-exchange backend.

    State machine: CREATED -> STARTING -> {READY, FAILED};
    {CREATED, READY, FAILED} -> SHUTDOWN. FAILED and SHUTDOWN are terminal --
    a Store cannot be restarted once it lands in either; construct a new
    instance instead.

    start()/shutdown() each run their body under a single per-instance lock,
    which is what makes repeated/concurrent calls idempotent and the
    terminal-state guard correct without any state duplicated in subclasses.
    """

    def __init__(self) -> None:
        self._state: StoreState = StoreState.CREATED
        self._endpoints: list[Endpoint] = []
        self._lock = asyncio.Lock()

    @property
    def state(self) -> StoreState:
        return self._state

    @property
    def endpoints(self) -> list[Endpoint]:
        if self._state is not StoreState.READY:
            raise StoreNotReadyError(
                f"{type(self).__name__} is not ready (state={self._state.name}); "
                "call `await store.start()` first."
            )
        return list(self._endpoints)

    async def ready(self) -> bool:
        if self._state is not StoreState.READY:
            return False
        return await self._do_ready()

    async def start(self, wait: bool = True) -> "Store":
        """Start the backend and return self, so both
        `await store.start()` and `store = await RedisStore(...).start()`
        work."""
        async with self._lock:
            if self._state in _TERMINAL_STATES:
                raise StoreTerminatedError(
                    f"{type(self).__name__} is in terminal state "
                    f"{self._state.name} and cannot be started again; "
                    "construct a new Store instance instead."
                )
            if self._state is StoreState.READY:
                return self
            self._state = StoreState.STARTING
            try:
                endpoints = await self._do_start(wait=wait)
            except BaseException as exc:
                self._state = StoreState.FAILED
                self._endpoints = []
                if isinstance(exc, StoreError) or not isinstance(exc, Exception):
                    # Already a StoreError, or a BaseException we must not
                    # mask (CancelledError, KeyboardInterrupt, SystemExit).
                    raise
                raise StoreStartupError(
                    f"{type(self).__name__} failed to start"
                ) from exc
            else:
                self._endpoints = list(endpoints)
                self._state = StoreState.READY
                return self

    async def shutdown(self) -> "Store":
        """Tear down the backend and return self, for the same fluent
        usage as start()."""
        async with self._lock:
            if self._state is StoreState.SHUTDOWN:
                return self
            try:
                await self._do_shutdown()
            finally:
                self._state = StoreState.SHUTDOWN
                self._endpoints = []
            return self

    @abc.abstractmethod
    async def _do_start(self, wait: bool) -> list[Endpoint]:
        """Launch the backend and return its endpoint(s). Raise on failure
        after cleaning up any partially-started state."""

    @abc.abstractmethod
    async def _do_shutdown(self) -> None:
        """Tear down the backend. Must tolerate being called with empty or
        partial internal state (never-started, or a failed start)."""

    @abc.abstractmethod
    async def _do_ready(self) -> bool:
        """Live readiness check, never cached."""
