"""
DragonStore-managed data exchange -- single-file example.

Architecture
────────────
  This mirrors example/py-cpp-exchange/dragon/driver.py, but instead of the
  driver manually constructing/serializing/destroying a `dragon.data.ddict.DDict`
  itself, RADEX's `DragonStore` owns that lifecycle:

    DragonStore.start()     -> constructs the DDict, blocks until ready
    DragonStore.endpoints   -> [DragonEndpoint(descriptor=...)]
    DragonStore.shutdown()  -> destroys the DDict

  DragonStore never constructs a client itself -- a real
  radex.clients.core.DragonClient is built directly from the endpoint's
  serialized descriptor, below.

  The serialized descriptor (`store.endpoints[0].serialize()`) is what you'd
  hand to a separately-launched process (env var, task kwarg, etc.) -- the
  Store itself never touches os.environ, so that handoff is always explicit.

Run with:
    dragon -s -- python driver.py
"""

import asyncio
import os
import pathlib
import time

import numpy as np
from dragon.native.process import Process, ProcessTemplate

from radex import DragonStore
from radex.clients.core import DragonClient
from radex.handles.handles import IncomingHandle, OutgoingHandle

HERE = pathlib.Path(__file__).parent.absolute()
ROOT = HERE.parent.parent.parent
EXAMPLES_BIN_DIR = ROOT / "install" / "bin" / "examples"


async def main() -> int:
    # ── 1. RADEX starts and owns the DDict-backed store ─────────────────────
    store = DragonStore(managers_per_node=1, n_nodes=1)
    await store.start()
    print(f"[Driver] DragonStore ready: {store.endpoints[0].serialize()[:32]}...")

    # ── 2. RADEX client, built directly from the endpoint's descriptor --
    #      Store never constructs clients itself ─────────────────────────
    client = DragonClient(descriptor=store.endpoints[0].serialize(), timeout=5)

    try:
        # ── 3. Hand the serialized descriptor to a separately-launched
        #      process -- the store never sets env vars for you.
        app_tmpl = ProcessTemplate(
            target=os.fspath(EXAMPLES_BIN_DIR / "dragon-cpp-with-py"),
            env={"SERIALIZED_DDICT": store.endpoints[0].serialize()},
        )
        app = Process.from_template(app_tmpl)

        print("[Driver] Starting C++ app")
        app.start()
        try:
            time.sleep(3)
            print("[Driver] Setting Int")
            client.put_scalar(OutgoingHandle("py-int"), 123)

            time.sleep(3)
            print("[Driver] Setting Double")
            client.put_scalar(OutgoingHandle("py-double"), 9.87)

            time.sleep(3)
            print("[Driver] Setting Numpy Float")
            client.put_scalar(OutgoingHandle("py-np-float"), np.float32(45.6))

            time.sleep(3)
            print("[Driver] Setting Int Tensor")
            client.put_tensor(OutgoingHandle("py-int-tensor"), np.arange(4, dtype=np.int32))

            time.sleep(3)
            print("[Driver] Setting Float Tensor")
            client.put_tensor(
                OutgoingHandle("py-float-tensor"),
                np.arange(12, dtype=np.float64).reshape((6, 2)),
            )

            print("[Driver] Looking for keys")
            print_scalar(client, "cpp-double")
            print_scalar(client, "cpp-int")
            print_tensor(client, "cpp-double-tensor")
            print_tensor(client, "cpp-long-tensor")
        finally:
            app.join()
    finally:
        # ── 4. RADEX owns teardown too -- idempotent, safe to call again.
        await store.shutdown()
        print(f"[Driver] Store state: {store.state.name}")

    return 0


def print_scalar(client, key):
    print(f"[Driver] Waiting for scalar key `{key}`")
    scalar = client.wait_for_scalar(IncomingHandle(key), 10)
    print(f"[Driver] Got scalar: {scalar}")


def print_tensor(client, key):
    print(f"[Driver] Waiting for tensor key `{key}`")
    tensor = client.wait_for_tensor(IncomingHandle(key), 10)
    print(f"[Driver] Got tensor: {tensor.ravel()}")


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
