from __future__ import annotations

import collections.abc as c_abc
import dataclasses
import functools
import typing as t

from flask import Response, jsonify, make_response
from radex.data._types import WorkflowSpecType, WorkflowIterableType

type _RequiresHandleRegistryFnType[**P, T] = c_abc.Callable[
    t.Concatenate["HandleRegistry", P], T
]
type _RequiresHandleRegistryFactoryReturnType[**P, T] = c_abc.Callable[P, T | Response]
type _RequiresHandleRegistryFactoryType[**P, T] = c_abc.Callable[
    [_RequiresHandleRegistryFnType[P, T]],
    _RequiresHandleRegistryFactoryReturnType[P, T],
]


@dataclasses.dataclass(frozen=True)
class HandleRegistry:
    handles: t.Collection[t.Any]

    @classmethod
    def from_spec(cls, spec: WorkflowSpecType) -> t.Self:
        return cls._from_iterable(self, spec.items())

    @classmethod
    def _from_iterable(cls, iterable: WorkflowIterableType) -> t.Self: ...

    def find(self) -> _ChainedIterable[t.Any]:
        return _filter(iter(self._items))

    def as_spec(self) -> WorkflowSpecType:
        ...


@dataclasses.dataclass(frozen=True)
class _ChainedIterable[T]:
    _items: t.Iterable[T]

    def collect(self) -> list[T]:
        return list(self.as_iterable())

    def as_iterable() -> t.Iterable[T]:
        return self._items

    def filter(self, predicate: c_abc.Callable[[T], bool]) -> t.Self:
        return type(self)(item for item in self.as_iterable() if predicate(item))

    def map[U](self, fn: c_abc.Callable[[T], U]) -> _ChainedIterable[U]:
        return type(self)(fn(item) for item in self.as_iterable())



_GLOBAL_REGISTRY: t.Final = HandleRegistry()


@t.overload
def requires_registry[**P, T](
    fn: _RequiresHandleRegistryFnType[P, T], /
) -> _RequiresHandleRegistryFactoryReturnType[P, T]: ...
@t.overload
def requires_registry[**P, T](fn: None = ..., /) -> c_abc.Callable[
    [_RequiresHandleRegistryFnType[P, T]],
    _RequiresHandleRegistryFactoryReturnType[P, T],
]: ...
def requires_registry[**P, T](
    fn: _RequiresHandleRegistryFnType[P, T] | None = None, /
) -> (
    _RequiresHandleRegistryFactoryType[P, T]
    | _RequiresHandleRegistryFactoryReturnType[P, T]
):
    def _provide_registry(
        f: _RequiresHandleRegistryFnType[P, T],
    ) -> _RequiresHandleRegistryFactoryReturnType[P, T]:
        def _with_registry(*args: P.args, **kwargs: P.kwargs) -> T | Response:
            registry = _GLOBAL_REGISTRY
            if registry is None:
                return make_response(
                    jsonify({"error": "Handle registry has not been initialized"}), 404
                )
            return f(registry, *args, **kwargs)

        return _with_registry

    if fn is None:
        return _provide_registry
    return _provide_registry(fn)
