from __future__ import annotations

import atexit
import collections.abc as c_abc
import os
import pathlib
import subprocess as sp
import time

from radex.data.manager import configure_data_manager_cmd

HERE = pathlib.Path(__file__).parent


def main() -> int:
    dm_config = configure_data_manager_cmd()

    with sp.Popen(dm_config.command) as dm_proc:
        with sp.Popen(
            ["mpirun", "my_cool_app"], env={"DM_HOST": ..., "DM_PORT": ...}
        ) as mpi_app:
            ...

    return 0


def launch_app(cmd: c_abc.Sequence[str]) -> c_abc.Callable[[dict[str, str]], sp.Popen]:
    def _luanch_app(env: dict[str, str]) -> sp.Popen:
        return sp.Popen(cmd, env={**os.environ, **env})

    return _launch_app


if __name__ == "__main__":
    raise SystemExit(main())
