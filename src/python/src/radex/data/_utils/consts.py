from __future__ import annotations

import typing as t

MNGR_ENTRYPOINT_MODULE: t.Final = "radex.data._entrypoint"
MNGR_ENTRYPOINT_ARGS_HOST: t.Final = ("--hostname",)
MNGR_ENTRYPOINT_ARGS_PORT: t.Final = ("--port",)
MNGR_ENTRYPOINT_ARGS_INIT_API_TIMEOUT: t.Final = ("--timeout",)
MNGR_ENTRYPOINT_ARGS_SPEC: t.Final = ("--spec",)

MNGR_APPLICATION: t.Final = "radex.data._application:app"

MNGR_MANAGED_APP_NAME: t.Final = "RADEX_DATA_MANAGER_PROCESS_NAME"
MNGR_HOST_ENV_VAR: t.Final = "RADEX_DATA_MANAGER_HOST"
MNGR_PORT_ENV_VAR: t.Final = "RADEX_DATA_MANAGER_PORT"
