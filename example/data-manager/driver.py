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
                        {"handle": "some-data-0", "dtype": "float32"},
                        {"handle": "some-data-1", "dtype": "float32"},
                        {"handle": "some-data-2", "dtype": "float32"},
                        {"handle": "some-data-3", "dtype": "float32"},
                    ],
                },
            },
            "consumer": {
                "scalars": {"incoming": [], "outgoing": []},
                "tensors": {
                    "incoming": [
                        {"handle": "some-data-0", "dtype": "float32"},
                        {"handle": "some-data-1", "dtype": "float32"},
                        {"handle": "some-data-2", "dtype": "float32"},
                        {"handle": "some-data-3", "dtype": "float32"},
                    ],
                    "outgoing": [],
                },
            },
        }
    ) as data_manager:
        for i in range(10):
            print("Doing work!! -> iter", i)
            time.sleep(1)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
