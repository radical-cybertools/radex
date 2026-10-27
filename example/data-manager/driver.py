from __future__ import annotations

import atexit
import collections.abc as c_abc
import os
import pathlib
import subprocess as sp
import time

from radex.data.manager import make_configuration as make_data_manager_configuration

HERE = pathlib.Path(__file__).parent


def main() -> int:
    dm_config = make_data_manager_configuration(
        {
            "producer": {
                "scalars": {"outgoing": []},
                "tensors": {
                    "outgoing": [
                        {"name": "some-data-0", "dtype": "float32"},
                        {"name": "some-data-1", "dtype": "float32"},
                        {"name": "some-data-2", "dtype": "float32"},
                        {
                            "short-name": "some-data-3",
                            "dtype": "float32",
                            "metadata": {},
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

    print("Command:", " ".join(dm_config.command))

    with sp.Popen(dm_config.command) as dm_proc:
        # with sp.Popen(
        #     ["mpirun", "my_cool_app"], env={"DM_HOST": ..., "DM_PORT": ...}
        # ) as mpi_app:
        #     ...
        time.sleep(120)
        proc.kill()

    return 0


def launch_app(cmd: c_abc.Sequence[str]) -> c_abc.Callable[[dict[str, str]], sp.Popen]:
    def _luanch_app(env: dict[str, str]) -> sp.Popen:
        return sp.Popen(cmd, env={**os.environ, **env})

    return _launch_app


if __name__ == "__main__":
    raise SystemExit(main())
