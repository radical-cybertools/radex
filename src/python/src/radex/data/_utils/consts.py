from __future__ import annotations

import typing as t

MNGR_ENTRYPOINT_MODULE: t.Final = "radex.data._entrypoint"
MNGR_APPLICATION: t.Final = "radex.data._application:app"

MNGR_MANAGED_APP_NAME: t.Final = "RADEX_DATA_MANAGER_PROCESS_NAME"
MNGR_HOST_ENV_VAR: t.Final = "RADEX_DATA_MANAGER_HOST"
MNGR_PORT_ENV_VAR: t.Final = "RADEX_DATA_MANAGER_PORT"
