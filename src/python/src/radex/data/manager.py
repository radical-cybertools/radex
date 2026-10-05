from __future__ import annotations

import collections.abc as c_abc
import contextlib
import dataclasses
import logging
import subprocess
import sys
import time
import typing as t

import requests
import requests.exceptions
from radex.data._types import ApplicationName, HandleDescription, ProcessDescription
from radex.handles.handles import IncomingHandle, OutgoingHandle

if t.TYPE_CHECKING:
    from types import TracebackType

    _T = t.TypeVar("_T")
    _EnvVarMapping = t.Mapping[str, str]

_LOGGER = logging.getLogger(__name__)


class DataManager(contextlib.AbstractContextManager):
    def __init__(
        self, info: _DataManagerInfo, *, max_connection_attempts: int = 60
    ) -> None:
        # TODO: use the info object to run the API on the correct port/host/etc
        self._application = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "radex.data._entrypoint",
                "--host",
                info.hostname,
                "--port",
                str(info.port),
            ]
        )
        self._driver = DataManagerDriver(info)

        waiting_for_server = True
        remaining_connection_attempts = max_connection_attempts
        failed_to_connect = RuntimeError("Failed to set up data manager server")
        while waiting_for_server and remaining_connection_attempts:
            try:
                res = requests.get(info.endpoint("/ping"))
            except requests.exceptions.ConnectionError:
                # Server not set up yet, try again
                _LOGGER.debug("Waiting for data manager server to start")
                remaining_connection_attempts -= 1
                time.sleep(1)
            else:
                if not res.ok:
                    self.stop()
                    raise failed_to_connect
                waiting_for_server = False
        if remaining_connection_attempts == 0:
            raise failed_to_connect

    @property
    def driver(self) -> DataManagerDriver:
        return self._driver

    def __enter__(self) -> DataManagerDriver:
        return self.driver

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.stop(timeout=None)

    @classmethod
    def initailize(
        cls, applications: dict[ApplicationName, ProcessDescription]
    ) -> t.Self:
        info = _DataManagerInfo(hostname="127.0.0.1", port=13254)
        self_ = cls(info=info)

        res = requests.post(info.endpoint("/init/workflow"), json=applications)
        if not res.ok:
            self_.stop()
            raise RuntimeError("Failed to initailize the data manager")

        return self_

    @classmethod
    def register_process(cls, application: str) -> DataManagedProcess:
        # TODO: what does this return
        # TODO: phone home to the data manager process so that it knows a
        #       process was started
        raise NotImplementedError("TODO: need to register a new proc")

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


@dataclasses.dataclass(frozen=True)
class _DataManagerInfo:
    hostname: str
    port: int

    @property
    def address(self) -> str:
        return f"http://{self.hostname}:{self.port}"

    def endpoint(self, route: str) -> str:
        sep = "" if route[0] == "/" else "/"
        return f"{self.address}{sep}{route}"


@dataclasses.dataclass(frozen=True)
class DataManagerDriver:
    info: _DataManagerInfo

    def start_process(self, name: str, how: c_abc.Callable[[_EnvVarMapping], _T]) -> _T:
        # TODO: What happens here?? What is reported to the server
        raise NotImplementedError("TODO")


@dataclasses.dataclass(frozen=True)
class DataManagedProcess:
    application: ApplicationName
    info: _DataManagerInfo

    def get_outgoing_handles(self, keys: c_abc.Sequence[str]) -> list[OutgoingHandle]:
        # TODO: this
        raise NotImplementedError("TODO")

    def get_incoming_handles(self, keys: c_abc.Sequence[str]) -> list[IncomingHandle]:
        # TODO: this
        raise NotImplementedError("TODO")
