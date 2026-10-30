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

from radex.data._application.handles.metadata import Metadata
from radex.data._types import (
    ApplicationName,
    HandleDescriptionType,
    ProcessDescription,
    WorkflowSpecType,
)
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

        def bind_namespace(
            namespace: argparse.Namespace,
        ) -> c_abc.Callable[[tuple[str, ...]], t.Any]:
            def _bound(flags: tuple[str, ...]) -> t.Any:
                return getattr(namespace, flags[0].lstrip("-"))

            return _bound

        get_val = bind_namespace(parser.parse_args(args))
        return cls(
            location=Locator(
                hostname=get_val(consts.MNGR_ENTRYPOINT_ARGS_HOST),
                port=get_val(consts.MNGR_ENTRYPOINT_ARGS_PORT),
            ),
            spec=get_val(consts.MNGR_ENTRYPOINT_ARGS_SPEC),
            timeout=get_val(consts.MNGR_ENTRYPOINT_ARGS_INIT_API_TIMEOUT),
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
    def command(self) -> tuple[str, ...]:
        return (
            sys.executable,
            "-m",
            consts.MNGR_ENTRYPOINT_MODULE,
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

    def await_api(self, timeout: int | None = None) -> None:
        waiting_for_server = True

        if timeout is None:
            remaining_connection_attempts = 1
            connect_attempts_decriment = 0
        else:
            remaining_connection_attempts = max(0, timeout)
            connect_attempts_decriment = 1

        while waiting_for_server and remaining_connection_attempts:
            try:
                res = requests.get(self.endpoint("/ping"))
            except requests.exceptions.ConnectionError:
                # Server not set up yet, try again
                _LOGGER.debug("Waiting for data manager server to start")
                remaining_connection_attempts -= connect_attempts_decriment
                time.sleep(1)
            else:
                if not res.ok:
                    _LOGGER.debug("Attempting to kill the data manager server")
                    raise RuntimeError("Recieved bad return code from data manager")
                waiting_for_server = False

            if remaining_connection_attempts == 0:
                raise RuntimeError("Failed to connect to Data Manager before timeout")

    def is_initialized(self) -> bool:
        res = requests.get(self.endpoint("/spec/workflow"))
        return res.ok


@dataclasses.dataclass(frozen=True)
class ManagedApplication:
    application: ApplicationName
    manager: Locator

    @property
    def _endpoint_safe_appname(self) -> str:
        return parse.esacpe_for_url(self.application)

    def get_outgoing_handle(self, description: HandleDescriptionType) -> OutgoingHandle:
        handles = self._get_outgoing_handles(description)
        num_handles = len(handles)
        if num_handles > 1:
            raise ValueError("Handle description was not unique")
        if num_handles == 0:
            raise ValueError("Handle description did not match any handle")
        return handles[0]

    def _get_outgoing_handles(
        self, description: HandleDescriptionType
    ) -> list[OutgoingHandle]:
        endpoint = self.manager.endpoint(
            f"/key/writeable/{self._endpoint_safe_appname}"
        )

        payload: dict[str, str] = {}
        if (dtype := description.get("dtype")) is not None:
            payload["dtype"] = dtype
        if (metadata := description.get("metadata")) is not None:
            payload["metadata"] = Metadata(metadata).to_query_string()

        res = requests.get(endpoint, params=payload)
        if not res.ok:
            raise RuntimeError(
                "Got a bad response from the data manager: "
                f"Status code: {res.status_code} "
                f"Request body: {res.json()} "
            )

        return [
            parse.response_to_outgoing_handle(parse.json_to_handle_response(item))
            for item in res.json()
        ]

    def get_incoming_handles(
        self, description: HandleDescriptionType
    ) -> list[IncomingHandle]:
        # TODO: this
        raise NotImplementedError("TODO: Impl this method")
