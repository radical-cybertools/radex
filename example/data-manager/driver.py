from __future__ import annotations

import atexit
import os
import subprocess as sp
import time
import collections.abc as c_abc
import pathlib


from radex.data.manager import DataManager

HERE = pathlib.Path(__file__).parent


def main() -> int:
    dm_cmd, dm_env = DataManager.configure(
        applications={
            "producer": {
                "scalars": {"outgoing": []},
                "tensors": {
                    "outgoing": [
                        # Handles should be collected in the the root proc of
                        # an MPI app, don't assume that every rank is
                        # communicating with the DM. Not incorrect, but not
                        # needed to be performant
                        {"short-name": "some-data-0", "dtype": "float32"},
                        {"short-name": "some-data-1", "dtype": "float32"},
                        {"short-name": "some-data-2", "dtype": "float32"},
                        {
                            "short-name": "some-data-3",
                            "dtype": "float32",
                            # TODO: user defined kwargs
                            "metadata": {},
                        },
                    ],
                },
            },
            "consumer": {
                "scalars": {"outgoing": []},
                "tensors": {
                    # TODO: do consumers need to register what handles they
                    # would consume?? It would help with a "dry run" option,
                    # but it is not striclty need to know who is requesting
                    # what, just that it can be fullfilled an dtheis can be
                    # done at run time. Potentailly just need to know what each
                    # app produces
                    "outgoing": [],
                },
            },
        }
    )

    with sp.Popen(dm_cmd, env={**os.environ, dm_env}) as dm_proc:
        with sp.Popen(["mpirun", "my_cool_app"], env={
            "DM_HOST": ..., "DM_PORT": ...
        }) as mpi_app:
            ...


    return 0

def launch_app(cmd: c_abc.Sequence[str]) -> c_abc.Callable[[dict[str, str]], sp.Popen]:
    def _luanch_app(env: dict[str, str]) -> sp.Popen:
        return sp.Popen(cmd, env={**os.environ, **env})
    return _launch_app

if __name__ == "__main__":
    raise SystemExit(main())
