from __future__ import annotations

import collections.abc as c_abc
import typing as t

type _SupportedDtypeType = t.Literal["int32", "int64", "float32", "float64"]
type _MetadataType = dict[str, str]

ApplicationName = t.NewType("ApplicationName", str)


class ScalarHandleDescription(t.TypedDict):
    name: str
    dtype: _SupportedDtypeType
    metadata: _MetadataType


class TensorHandleDescription(t.TypedDict):
    name: str
    dtype: _SupportedDtypeType
    metadata: _MetadataType
    # TODO: Does a 'dimensions' key make sense? Seems like it could be useful,
    #       but currently we do not have a handle that would enforce this
    #       constraint at runtime :(
    # dims: list[int] | t.Literal["any"]


class _InOut[T](t.TypedDict):
    incoming: list[T]
    outgoing: list[T]


class ProcessDescription(t.TypedDict):
    scalars: _InOut[ScalarHandleDescription]
    tensors: _InOut[TensorHandleDescription]


type WorkflowSpecType = dict[ApplicationName, ProcessDescription]
type WorkflowIterableType = t.Iterable[tuple[ApplicationName, ProcessDescription]]
