from __future__ import annotations

import argparse
import collections.abc as c_abc
import contextlib
import logging
import subprocess
import sys
import time
import typing as t

import requests

from radex.data._types import JsonType, WorkflowSpecType
from radex.data._utils import consts, parse
from radex.data.manager import Configuration, Locator

if t.TYPE_CHECKING:
    from types import TracebackType

_LOGGER: t.Final = logging.Logger(__name__)

# TODO: make this dynamic
_LOGGER.setLevel(logging.DEBUG)


def main() -> int:
    config = Configuration.from_cli_args()
    with APIProcess(where=config.location) as proc:
        proc.await_api(config.timeout)
        proc.initialize_handle_spec(config.spec)

    if (ret_code := proc.returncode) is None:
        raise ValueError("Data manager return code was not set")
    return ret_code


class APIProcess(contextlib.AbstractContextManager["APIProcess"]):
    def __init__(self, where: Locator) -> None:
        self._locator = where
        self._application = subprocess.Popen(
            (
                sys.executable,
                "-m",
                "flask",
                "--app",
                consts.MNGR_APPLICATION,
                "run",
                "--host",
                self._locator.hostname,
                "--port",
                str(self._locator.port),
            ),
        )

    def __enter__(self) -> t.Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.stop(timeout=None)

    @property
    def returncode(self) -> int | None:
        return self._application.returncode

    def await_api(self, timeout: int) -> None:
        waiting_for_server = True
        remaining_connection_attempts = timeout
        failed_to_initialize = RuntimeError("Failed to initialize data manager server")

        while waiting_for_server and remaining_connection_attempts:
            try:
                res = requests.get(self._locator.endpoint("/ping"))
            except requests.exceptions.ConnectionError:
                # Server not set up yet, try again
                _LOGGER.debug("Waiting for data manager server to start")
                remaining_connection_attempts -= 1
                time.sleep(1)
            else:
                if not res.ok:
                    _LOGGER.debug("Attempting to kill the data manager server")
                    self._application.kill()
                    raise failed_to_initialize
                waiting_for_server = False

            if remaining_connection_attempts == 0:
                raise failed_to_initialize

    def initialize_handle_spec(self, spec: WorkflowSpecType) -> None:
        res = requests.post(
            self._locator.endpoint("/init/workflow"), json=parse.spec_to_json(spec)
        )
        if not res.ok:
            self.stop()
            raise RuntimeError("Failed to initailize the data manager")

    def stop(self, timeout: int | None = None) -> int:
        ret_code = self._application.poll()
        if ret_code is None:
            _LOGGER.debug("Attempting to kill the data manager server")
            self._application.kill()
            self._application.wait(timeout=timeout)
            ret_code = self._application.poll()
        if ret_code is None:
            raise ValueError("Data Manager return code was not set")
        return ret_code


if __name__ == "__main__":
    raise SystemExit(main())
