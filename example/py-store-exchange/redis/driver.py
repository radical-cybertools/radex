"""
RedisStore-managed data exchange -- single-file example.

Architecture
────────────
  RedisStore models N *independent* per-node Redis instances -- not a Redis
  Cluster. Each node is its own isolated keyspace; `store.endpoints` is a
  list with one RedisEndpoint per node.

  RedisStore never constructs a client itself. The typed RADEX client
  (`radex.clients.core.RedisClient` -- `put_scalar`/`get_scalar`/
  `put_tensor`/`get_tensor`, the same API `DragonClient` exposes) only
  supports env-based construction (no host/port constructor args), so a
  client for one specific endpoint is built by pointing
  `RADEX_STORE`/`RADEX_STORE_OPTS` at that endpoint first, then
  constructing `RedisClient()`:

      os.environ["RADEX_STORE"] = endpoint.serialize()
      os.environ["RADEX_STORE_OPTS"] = "Standalone"
      client = RedisClient()

  (For a raw redis-py client instead -- direct SET/GET, not RADEX's typed
  API -- use `RedisStore.client(index=...)`.)

  Locally, RedisStore() with no arguments spawns a single `redis-server` on
  an auto-picked free port -- this is what the first half of this example
  uses. The second half shows the same API scaled out to several
  independent local nodes, and how you'd point it at an HPC launcher
  instead (commented out, since it needs a real Slurm allocation to run):

    RedisStore(
        hosts=["nid00001", "nid00002", "nid00003"],
        port=6380,
        cmd="srun --nodelist={host} redis-server --port {port}",
    )

Run with:
    python driver.py
"""

import asyncio
import os

import numpy as np

from radex import RedisStore
from radex.clients.core import RedisClient
from radex.handles.handles import IncomingHandle, OutgoingHandle
from radex.store.redis_store import RedisEndpoint


def client_for(endpoint: RedisEndpoint) -> RedisClient:
    """Build a typed RADEX client bound to one specific endpoint.

    `RedisClient()` only constructs from the environment, so this points
    `RADEX_STORE`/`RADEX_STORE_OPTS` at `endpoint` first.
    """
    os.environ["RADEX_STORE"] = endpoint.serialize()
    os.environ["RADEX_STORE_OPTS"] = "Standalone"
    return RedisClient()


async def single_node_demo() -> None:
    print("── Single local node ──────────────────────────────────────────")
    store = RedisStore()
    await store.start()
    try:
        endpoint = store.endpoints[0]
        print(f"[Driver] RedisStore ready at {endpoint.serialize()}")

        client = client_for(endpoint)

        client.put_scalar(OutgoingHandle("greeting-count"), 1)
        count = client.get_scalar(IncomingHandle("greeting-count"))
        print(f"[Driver] Got scalar back: {count}")

        client.put_tensor(OutgoingHandle("samples"), np.arange(6, dtype=np.float64))
        samples = client.get_tensor(IncomingHandle("samples"))
        print(f"[Driver] Got tensor back: {samples}")

        print(f"[Driver] ready(): {await store.ready()}")
    finally:
        await store.shutdown()
        print(f"[Driver] Store state: {store.state.name}")


async def multi_node_demo() -> None:
    print("\n── Multiple independent local nodes ───────────────────────────")
    store = RedisStore(hosts=["localhost", "localhost", "localhost"])
    await store.start()
    try:
        print(f"[Driver] {len(store.endpoints)} independent nodes:")
        for i, endpoint in enumerate(store.endpoints):
            # Each node is its own keyspace -- write a distinct value to each.
            client = client_for(endpoint)
            client.put_scalar(OutgoingHandle("node-id"), i)
            node_id = client.get_scalar(IncomingHandle("node-id"))
            print(f"[Driver]   node {i}: {endpoint.serialize()} -> node-id={node_id}")
    finally:
        await store.shutdown()


async def main() -> int:
    await single_node_demo()
    await multi_node_demo()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
