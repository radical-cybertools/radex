from __future__ import annotations

import collections.abc as c_abc
import contextlib
import dataclasses
import logging
import os
import subprocess
import sys
import time
import typing as t

import requests
import requests.exceptions
from radex.data._types import ApplicationName, ProcessDescription
from radex.data._utils import consts, escape
from radex.handles.handles import IncomingHandle, OutgoingHandle

if t.TYPE_CHECKING:
    from types import TracebackType

    _EnvVarMapping = t.Mapping[str, str]

_LOGGER = logging.getLogger(__name__)


class DataManager(contextlib.AbstractContextManager["DataManagerDriver"]):
    def __init__(
        self, info: _DataManagerInfo, *, max_connection_attempts: int = 60
    ) -> None:
        # TODO: use the info object to run the API on the correct port/host/etc
        self._application = subprocess.Popen(
            [
                sys.executable,
                "-m",
                consts.MNGR_ENTRYPOINT_MODULE,
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
        info = _DataManagerInfo.from_environment()
        return DataManagedProcess(ApplicationName(application), info)

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

    def to_env_vars(self) -> dict[str, str]:
        return {
            consts.MNGR_HOST_ENV_VAR: self.hostname,
            consts.MNGR_PORT_ENV_VAR: str(self.port),
        }

    @classmethod
    def _from_str_mapping(cls, mapping: t.Mapping[str, str]) -> t.Self:
        def get_val[T](key: str, as_type: c_abc.Callable[[str], T]) -> T:
            try:
                val = mapping[key]
            except KeyError as e:
                raise ValueError(
                    f"Failed to find a value for `{key}` in provided mapping"
                ) from e
            return as_type(val)

        self_ = cls(
            hostname=get_val("RADEX_DATA_MANAGER_HOST", as_type=str),
            port=get_val("RADEX_DATA_MANAGER_PORT", as_type=int),
        )

        return self_

    @classmethod
    def from_environment(cls) -> t.Self:
        return cls._from_str_mapping(os.environ)


@dataclasses.dataclass(frozen=True)
class DataManagerDriver:
    info: _DataManagerInfo

    def start_process[T](
        self, name: str, how: c_abc.Callable[[_EnvVarMapping], T]
    ) -> T:
        # TODO: What happens here?? What is reported to the server
        raise NotImplementedError("TODO")


@dataclasses.dataclass(frozen=True)
class DataManagedProcess:
    application: ApplicationName
    info: _DataManagerInfo

    @property
    def _endpoint_safe_appname(self) -> str:
        return escape.url(self.application)

    def get_outgoing_handles(self, metadtaa) -> list[OutgoingHandle]:
        endpoint = self.info.endpoint(f"/key/writeable/{self._endpoint_safe_appname}")
        res = requests.get(endpoint)
        # TODO: What does `res` look like??
        # TODO: We probably need a way to search the outgoing handles for
        #       specific type/dtype/shape/etc. Maybe return a handle registry??
        return [OutgoingHandle(key) for key in []]

    def get_incoming_handles(self, keys: c_abc.Sequence[str]) -> list[IncomingHandle]:
        # TODO: this
        raise NotImplementedError("TODO")
