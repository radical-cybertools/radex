"""
RedisStore-managed data exchange -- single-file example.

Architecture
────────────
  RedisStore models N *independent* per-node Redis instances -- not a Redis
  Cluster. Each node is its own isolated keyspace; `store.endpoints` is a
  list with one RedisEndpoint per node, and each endpoint gets its own
  `.client()` (a plain redis-py `redis.Redis`).

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

  Store never mutates os.environ or the C++ SmartRedis env-var convention
  (RADEX_STORE/RADEX_STORE_OPTS) itself -- if you need the compiled
  `radex::redis::smartredis::Client` to attach to a node this Store
  launched, wire that through explicitly yourself, e.g.:

    os.environ["RADEX_STORE"] = store.endpoints[0].serialize()

Run with:
    python driver.py
"""

import asyncio

from radex import RedisStore


async def single_node_demo() -> None:
    print("── Single local node ──────────────────────────────────────────")
    store = RedisStore()
    await store.start()
    try:
        endpoint = store.endpoints[0]
        print(f"[Driver] RedisStore ready at {endpoint.serialize()}")

        client = store.client()
        client.set("greeting", "hello from RADEX")
        print(f"[Driver] Got back: {client.get('greeting').decode()}")
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
            client = endpoint.client()
            client.set("node-id", i)
            print(f"[Driver]   node {i}: {endpoint.serialize()} -> "
                  f"node-id={client.get('node-id').decode()}")
    finally:
        await store.shutdown()


async def main() -> int:
    await single_node_demo()
    await multi_node_demo()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
