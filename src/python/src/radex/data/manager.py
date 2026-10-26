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
    _EnvVarMapping = t.Mapping[str, str]

_LOGGER = logging.getLogger(__name__)


def make_configuration(
    spec: WorkflowSpecType, where: Locator | None = None, timeout: int = 60
) -> Configuration:
    return Configuration(
        location=where if where is not None else Locator.default(),
        spec=spec,
        timeout=timeout,
    )


@dataclasses.dataclass(frozen=True)
class Configuration:
    location: Locator
    spec: WorkflowSpecType
    timeout: int

    @classmethod
    def from_cli_args(cls, args: c_abc.Sequence[str] | None = None) -> t.Self:
        parser = argparse.ArgumentParser()
        parser.add_argument(*consts.MNGR_ENTRYPOINT_ARGS_HOST, type=str, required=True)
        parser.add_argument(*consts.MNGR_ENTRYPOINT_ARGS_PORT, type=int, required=True)
        parser.add_argument(
            *consts.MNGR_ENTRYPOINT_ARGS_INIT_API_TIMEOUT, type=int, required=True
        )
        parser.add_argument(
            *consts.MNGR_ENTRYPOINT_ARGS_SPEC, type=parse.spec_from_str, required=True
        )

        ns = parser.parse_args(args)
        return cls(
            location=Locator(hostname=ns.host, port=ns.port),
            spec=ns.spec,
            timeout=ns.timeout,
        )

    @property
    def cli_args(self) -> tuple[str, ...]:
        return (
            consts.MNGR_ENTRYPOINT_ARGS_HOST[0],
            self.location.hostname,
            consts.MNGR_ENTRYPOINT_ARGS_PORT[0],
            str(self.location.port),
            consts.MNGR_ENTRYPOINT_ARGS_INIT_API_TIMEOUT[0],
            str(self.timeout),
            consts.MNGR_ENTRYPOINT_ARGS_SPEC[0],
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

    @classmethod
    def default(cls) -> t.Self:
        return cls(hostname="127.0.0.1", port=27072)

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
