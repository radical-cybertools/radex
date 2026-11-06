from __future__ import annotations

import atexit
import collections.abc as c_abc
import contextlib
import os
import pathlib
import shutil
import subprocess as sp
import sys
import time

from dragon.data.ddict import DDict
from dragon.native.process import Process, ProcessTemplate

from radex.data.manager import make_configuration as make_data_manager_configuration

HERE = pathlib.Path(__file__).parent


def main() -> int:
    dm_config = make_data_manager_configuration(
        {
            "producer": {
                "scalars": {"outgoing": []},
                "tensors": {
                    "outgoing": [
                        {
                            "name": "some-data-0",
                            "dtype": "float32",
                            "metadata": {"which-rank": "0"},
                        },
                        {
                            "name": "some-data-1",
                            "dtype": "float32",
                            "metadata": {"which-rank": "1"},
                        },
                        {
                            "name": "some-data-2",
                            "dtype": "float32",
                            "metadata": {"which-rank": "2"},
                        },
                        {
                            "name": "some-data-3",
                            "dtype": "float32",
                            "metadata": {"which-rank": "3"},
                        },
                    ],
                },
            },
            "consumer": {
                "scalars": {"outgoing": []},
                "tensors": {"outgoing": []},
            },
        }
    )

    dd = DDict(
        managers_per_node=1,
        n_nodes=1,
        trace=False,
        wait_for_keys=True,
        working_set_size=3,
    )

    env = {
        **os.environ,
        **dm_config.location.to_env_vars(),
        "SERIALIZED_DDICT": dd.serialize(),
    }

    with sp.Popen(dm_config.command) as data_manager:
        producer = Process(
            target=sys.executable, args=[os.fspath(HERE / "producer.py")], env=env
        )
        consumer = Process(
            target=sys.executable, args=[os.fspath(HERE / "consumer.py")], env=env
        )

        try:
            print("PRODUCER: starting procs")
            producer.start()
            consumer.start()
            print("PRODUCER: procs started")
        finally:
            print("PRODUCER: awaiting procs")
            producer.join()
            consumer.join()
            print("PRODUCER: procs joined")

        print("PRODUCER: terminateing server")
        data_manager.terminate()
        print("PRODUCER: server terminated")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
