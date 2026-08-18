from __future__ import annotations

import asyncio
import dataclasses
from typing import Any, Mapping

from radex.store.base import Endpoint, Store, StoreStartupError

try:
    import dragon  # noqa: F401
    from dragon.data.ddict import DDict as _DDict
except ImportError:  # pragma: no cover - environment without Dragon
    dragon = None
    _DDict = None


_PROBE_KEY = "__radex_store_liveness_probe__"


@dataclasses.dataclass(frozen=True)
class DragonEndpoint(Endpoint):
    """Connection information for a Dragon DDict-backed store.

    Unlike Redis, there is no host/port here -- `serialize()` returns the
    opaque base64 descriptor produced by `DDict.serialize()`, which is what
    both the compiled `radex::drg::ddict::Client` and `DDict.attach()` expect.
    """

    descriptor: str

    def serialize(self) -> str:
        return self.descriptor

    def client(self, *, timeout: int = 5) -> Any:
        # Deferred import: radex.store must stay importable even when the
        # compiled radex.clients.core extension isn't available/built.
        from radex.clients.core import DragonClient

        return DragonClient(descriptor=self.descriptor, timeout=timeout)


class DragonStore(Store):
    """A Store backed by a single Dragon DDict.

    Constructing a `dragon.data.ddict.DDict` is itself the blocking startup
    call -- it spins up the orchestrator and manager processes and blocks
    until ready, with no separate "start" step. This wraps that blocking
    call in `asyncio.to_thread`, matching Dragon's own established
    convention for calling blocking Dragon primitives from asyncio.

    `wait_for_keys` is hard-enforced to True: the compiled
    `radex::drg::ddict::Client` (`include/radex/dragon.hpp`, `_validate_ddict`
    in `src/cpp/dragon.cpp`) refuses to attach to a DDict created with
    `wait_for_keys=False`, so any other value would guarantee every
    downstream C++/Cython client fails to construct.
    """

    def __init__(
        self,
        managers_per_node: int = 1,
        n_nodes: int = 1,
        total_mem: int | None = None,
        *,
        working_set_size: int = 2,
        wait_for_keys: bool = True,
        wait_for_writers: bool = False,
        policy: Any = None,
        managers_per_policy: int = 1,
        orc_policy: Any = None,
        persist_freq: int = 0,
        name: str = "",
        timeout: float | None = None,
        trace: bool = False,
        streams_per_manager: int = 5,
        manager_pool_full_thresh: float = 0.9,
        extra_ddict_kwargs: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__()
        if _DDict is None:
            raise ImportError(
                "The 'dragon' package is required to use DragonStore. It is "
                "not pip-installable from PyPI; install it per your Dragon "
                "distribution/environment first."
            )
        if wait_for_keys is not True:
            raise ValueError(
                "DragonStore requires wait_for_keys=True: the compiled "
                "radex::drg::ddict::Client (include/radex/dragon.hpp, "
                "_validate_ddict) refuses to attach to a DDict created with "
                "wait_for_keys=False, so every downstream C++/Cython client "
                "would immediately fail to construct."
            )
        if working_set_size < 2:
            raise ValueError(
                "DragonStore requires working_set_size >= 2 when combined "
                "with the (always-forced) wait_for_keys=True: DDict itself "
                "rejects wait_for_keys=True with working_set_size < 2."
            )

        self._ddict_kwargs: dict[str, Any] = dict(
            managers_per_node=managers_per_node,
            n_nodes=n_nodes,
            working_set_size=working_set_size,
            wait_for_keys=True,
            wait_for_writers=wait_for_writers,
            policy=policy,
            managers_per_policy=managers_per_policy,
            orc_policy=orc_policy,
            persist_freq=persist_freq,
            name=name,
            timeout=timeout,
            trace=trace,
            streams_per_manager=streams_per_manager,
            manager_pool_full_thresh=manager_pool_full_thresh,
        )
        if total_mem is not None:
            self._ddict_kwargs["total_mem"] = total_mem
        self._ddict_kwargs.update(extra_ddict_kwargs or {})
        self._ddict: Any = None

    async def _do_start(self, wait: bool) -> list[Endpoint]:
        # `wait` is accepted for interface parity with Store.start() but has
        # no effect: DDict.__init__ is already atomically blocking-until-
        # ready -- there is no separate "start" step to skip waiting on.
        try:
            self._ddict = await asyncio.to_thread(_DDict, **self._ddict_kwargs)
        except Exception as exc:
            self._ddict = None
            raise StoreStartupError(
                f"DragonStore failed to construct DDict: {exc}"
            ) from exc
        return [DragonEndpoint(descriptor=self._ddict.serialize())]

    async def _do_shutdown(self) -> None:
        if self._ddict is not None:
            await asyncio.to_thread(self._ddict.destroy)
        self._ddict = None

    async def _do_ready(self) -> bool:
        if self._ddict is None:
            return False

        def _probe() -> bool:
            try:
                _ = _PROBE_KEY in self._ddict
                return True
            except Exception:
                return False

        return await asyncio.to_thread(_probe)
