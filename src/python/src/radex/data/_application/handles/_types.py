from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    from radex.data._application.handles.metadata import Metadata
    from radex.data._types import ApplicationName


class HandleRegistryEntry(t.Protocol):
    name: str
    from_app: ApplicationName
    dtype: str
    metadata: Metadata
