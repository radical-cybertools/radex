from __future__ import annotations

import dataclasses
import typing as t

from radex.data._application.handles._types import HandleRegistryEntry
from radex.data._application.handles.metadata import Metadata
from radex.data._types import ApplicationName, ScalarHandleDescription


@dataclasses.dataclass(frozen=True)
class ScalarHandleRegistryEntry(HandleRegistryEntry):
    name: str
    from_app: ApplicationName
    dtype: str
    metadata: Metadata

    @classmethod
    def from_spec(
        cls, from_app: ApplicationName, spec: ScalarHandleDescription
    ) -> t.Self:
        return cls(
            from_app=from_app,
            name=spec["name"],
            dtype=spec["dtype"],
            metadata=Metadata.from_mapping(spec["metadata"]),
        )
