from __future__ import annotations

import argparse
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
from radex.data._types import ApplicationName, ProcessDescription, WorkflowSpecType
from radex.data._utils import consts, parse
from radex.handles.handles import IncomingHandle, OutgoingHandle

if t.TYPE_CHECKING:
    from types import TracebackType

    _EnvVarMapping = t.Mapping[str, str]

_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class Configuration:
    location: Locator
    spec: WorkflowSpecType
    timeout: int

    @classmethod
    def from_cli_args(cls) -> t.Self:
        parser = argparse.ArgumentParser()
        parser.add_argument("--host", type=str, required=True)
        parser.add_argument("--port", type=int, required=True)
        parser.add_argument("--timeout", type=int, required=True)
        parser.add_argument("--spec", type=parse.spec_from_str, required=True)

        args = parser.parse_args()
        return cls(
            location=Locator(hostname=args.host, port=args.port),
            spec=args.spec,
            timeout=args.timeout,
        )

    @property
    def cli_args(self) -> tuple[str, ...]:
        return (
            "--host",
            self.location.hostname,
            "--port",
            str(self.location.port),
            "--timeout",
            str(self.timeout),
            "--spec",
            parse.spec_to_str(self.spec),
        )

    @property
    def commnad(self) -> tuple[str, ...]:
        return (
            sys.executable,
            "-m",
            consts.MNGR_ENTRYPOINT_MODULE,
            "--",
            *self.cli_args,
        )


@dataclasses.dataclass(frozen=True)
class Locator:
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
            hostname=get_val(consts.MNGR_HOST_ENV_VAR, as_type=str),
            port=get_val(consts.MNGR_PORT_ENV_VAR, as_type=int),
        )

        return self_

    @classmethod
    def from_environment(cls) -> t.Self:
        return cls._from_str_mapping(os.environ)


@dataclasses.dataclass(frozen=True)
class ManagedApplication:
    application: ApplicationName
    info: Locator

    @property
    def _endpoint_safe_appname(self) -> str:
        return parse.esacpe_for_url(self.application)

    def get_outgoing_handles(self) -> list[OutgoingHandle]:
        endpoint = self.info.endpoint(f"/key/writeable/{self._endpoint_safe_appname}")
        res = requests.get(endpoint)
        # TODO: What does `res` look like??
        # TODO: We probably need a way to search the outgoing handles for
        #       specific type/dtype/shape/etc. Maybe return a handle registry??
        return []

    def get_incoming_handles(
        self, metadata: c_abc.Sequence[str]
    ) -> list[IncomingHandle]:
        # TODO: this
        raise NotImplementedError("TODO")
