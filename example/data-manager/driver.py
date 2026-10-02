from __future__ import annotations

import atexit
from radex.data.manager import DataManager
import requests
import time

def clean_up_data_manager(proc):
    # TODO: This should not be defined in the driver
    proc.kill()
    proc.wait()
    return proc.returncode

def main() -> int:
    proc, data_manager = DataManager.initailize(
        applications={
            "producer": {
                "incoming": [],
                "outgoing": [
                    {"handle": "some-data-0", "dtype": "float32", "dims": "tensor"},
                    {"handle": "some-data-1", "dtype": "float32", "dims": "tensor"},
                    {"handle": "some-data-2", "dtype": "float32", "dims": "tensor"},
                    {"handle": "some-data-3", "dtype": "float32", "dims": "tensor"},
                ],
            },
            "consumer": {
                "incoming": [
                    {"handle": "some-data-0", "dtype": "float32", "dims": "tensor"},
                    {"handle": "some-data-1", "dtype": "float32", "dims": "tensor"},
                    {"handle": "some-data-2", "dtype": "float32", "dims": "tensor"},
                    {"handle": "some-data-3", "dtype": "float32", "dims": "tensor"},
                ],
                "outgoing": [],
            },
        }
    )

    # FIXME: This should not be done in the driver
    atexit.register(clean_up_data_manager, proc)

    time.sleep(5)
    res = requests.post("http://127.0.0.1:13254/init/workflow", json={"hello": "world-1"})
    print("Got status:", res.status_code)
    print("Got body:", res.text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
