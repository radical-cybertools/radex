from __future__ import annotations

import subprocess
import sys
import typing as t

import requests
from radex.data._types import ApplicationName, HandleDescription, ProcessDescription


class DataManager:
    def __init__(self, hostname: str, port: int) -> None:
        self._hostname = hostname
        self._port = port

    @property
    def address(self) -> str:
        return f"{self._hostname}:{self._port}"

    @classmethod
    def initailize(
        cls, applications: dict[ApplicationName, ProcessDescription]
    ) -> tuple[subprocess.Popen, t.Self]:
        proc = subprocess.Popen([sys.executable, "-m", "radex.data._entrypoint"])

        # FIXME: do not like that the proc for the DM is outside of the DM
        #        class, but I also want to make the DM just a client that can
        #        be used by managed procs. Maybe change this?? For now, just
        #        return the proc as is
        return proc, cls(hostname="127.0.0.1", port=13254)

    @classmethod
    def init_process(
        cls,
        /,
        application: str,
        supplies: list[HandleDescription],
        requires: list[HandleDescription],
    ) -> ManagedProcess:
        # TODO: what does this return
        # TODO: phone home to the data manager process so that it knows a
        #       process was started
        return ManagedProcess(parent=self, application=ApplicationName(application))

    def start_process(self, name: str) -> t.Any:
        # TODO: What happens here??
        # TODO: What is the return value here
        ...


class ManagedProcess:
    def __init__(self, parent: DataManager, application: ApplicationName) -> None:
        self._parent = parent
        self._application = application
