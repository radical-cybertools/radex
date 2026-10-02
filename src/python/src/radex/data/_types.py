from __future__ import annotations

import typing as t

_DimensionalityType = t.Literal["scalar", "tensor"]
_SupportedType: t.TypeAlias = t.Literal["int32", "int64", "float32", "float64"]

ApplicationName = t.NewType("ApplicationName", str)


class HandleDescription(t.TypedDict):
    handle: str
    dims: _DimensionalityType
    dtype: _SupportedType


class ProcessDescription(t.TypedDict):
    incoming: HandleDescription
    outgoing: HandleDescription
