from __future__ import annotations

import atexit
import collections.abc as c_abc
import contextlib
import os
import pathlib
import subprocess as sp
import sys
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

    with sp.Popen(dm_config.command) as data_manager:
        with contextlib.ExitStack() as ctx:
            producer = ctx.enter_context(
                sp.Popen(
                    [sys.executable, os.fspath(HERE / "producer.py")],
                    env={**os.environ, **dm_config.location.to_env_vars()},
                )
            )
        print("DRIVER:", "waiting 2 minutes")
        time.sleep(120)
        print("DRIVER:", "All done, terminating DM")
        data_manager.terminate()

    return 0


def launch_app(cmd: c_abc.Sequence[str]) -> c_abc.Callable[[dict[str, str]], sp.Popen]:
    def _luanch_app(env: dict[str, str]) -> sp.Popen:
        return sp.Popen(cmd, env={**os.environ, **env})

    return _launch_app


if __name__ == "__main__":
    raise SystemExit(main())
