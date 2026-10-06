from __future__ import annotations

import typing as t

_T = t.TypeVar("_T")

_DimensionalityType = t.Literal["scalar", "tensor"]
_SupportedType: t.TypeAlias = t.Literal["int32", "int64", "float32", "float64"]

ApplicationName = t.NewType("ApplicationName", str)


class ScalarHandleDescription(t.TypedDict):
    handle: str
    dtype: _DimensionalityType


class TensorHandleDescription(t.TypedDict):
    handle: str
    dtype: _DimensionalityType
    # TODO: Does a 'dimensions' key make sense? Seems like it could be useful,
    #       but currently we do not have a handle that would enforce this
    #       constraint at runtime :(
    # dims: list[int] | t.Literal["any"]


class _InOut(t.TypedDict, t.Generic[_T]):
    incoming: list[_T]
    outgoing: list[_T]


class ProcessDescription(t.TypedDict):
    scalars: _InOut[ScalarHandleDescription]
    tensors: _InOut[TensorHandleDescription]
