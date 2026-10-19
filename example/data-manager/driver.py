from __future__ import annotations

import atexit
import time

from radex.data.manager import DataManager


def main() -> int:
    with DataManager.initailize(
        applications={
            "producer": {
                "scalars": {"incoming": [], "outgoing": []},
                "tensors": {
                    "incoming": [],
                    "outgoing": [
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
                "scalars": {"incoming": [], "outgoing": []},
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
    ) as data_manager:
        for i in range(10):
            print("Doing work!! -> iter", i)
            time.sleep(1)

    return 0

def launch_app(cmd: c_abc.Sequence[str]) -> c_abc.Callable[[dict[str, str]], sp.Popen]:
    def _luanch_app(env: dict[str, str]) -> sp.Popen:
        return sp.Popen(cmd, env={**os.environ, **env})
    return _launch_app

if __name__ == "__main__":
    raise SystemExit(main())
