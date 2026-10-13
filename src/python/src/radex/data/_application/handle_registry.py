from __future__ import annotations

import collections.abc as c_abc
import dataclasses
import functools
import itertools
import typing as t

from flask import Response, jsonify, make_response
from radex.data._types import (
    ApplicationName,
    ScalarHandleDescription,
    TensorHandleDescription,
    WorkflowIterableType,
    WorkflowSpecType,
)


@dataclasses.dataclass(frozen=True)
class HandleRegistry:
    scalars: t.Collection[ScalarHandleRegistryEntry]
    tensors: t.Collection[TensorHandleRegistryEntry]

    @property
    def handles(self) -> c_abc.Iterable[_HandleRegistryEntry]:
        return itertools.chain(self.scalars, self.tensors)

    @classmethod
    def from_spec(cls, spec: WorkflowSpecType) -> t.Self:
        return cls._from_iterable(spec.items())

    @classmethod
    def _from_iterable(cls, iterable: WorkflowIterableType) -> t.Self:
        iter1, iter2 = itertools.tee(iterable)
        scalars = [
            ScalarHandleRegistryEntry.from_spec(from_app=app, spec=desc)
            for app, proc_desc in iter1
            for desc in proc_desc["scalars"]["outgoing"]
        ]
        tensors = [
            TensorHandleRegistryEntry.from_spec(from_app=app, spec=desc)
            for app, proc_desc in iter2
            for desc in proc_desc["tensors"]["outgoing"]
        ]

        return cls(scalars, tensors)

    def find(self) -> _HandleRegistryEntryIterable:
        return _HandleRegistryEntryIterable(iter(self.handles))


@dataclasses.dataclass(frozen=True)
class _HandleRegistryEntry:
    name: str
    from_app: ApplicationName
    dtype: str
    metadata: dict[str, str]


class ScalarHandleRegistryEntry(_HandleRegistryEntry):
    @classmethod
    def from_spec(
        cls, from_app: ApplicationName, spec: ScalarHandleDescription
    ) -> t.Self:
        return cls(from_app=from_app, **spec)


class TensorHandleRegistryEntry(_HandleRegistryEntry):
    @classmethod
    def from_spec(
        cls, from_app: ApplicationName, spec: TensorHandleDescription
    ) -> t.Self:
        return cls(from_app=from_app, **spec)


@dataclasses.dataclass(frozen=True)
class _ChainedIterable[T]:
    _items: t.Iterable[T]

    def collect(self) -> list[T]:
        return list(self.as_iterable())

    def collect_or[U](self, fallback: U) -> list[T] | U:
        try:
            return self.collect()
        except Exception:
            return fallback

    def as_iterable(self) -> t.Iterable[T]:
        return self._items

    def filter(self, predicate: c_abc.Callable[[T], bool]) -> t.Self:
        return type(self)(item for item in self.as_iterable() if predicate(item))

    def map[U](self, fn: c_abc.Callable[[T], U]) -> _ChainedIterable[U]:
        return _ChainedIterable(fn(item) for item in self.as_iterable())


class _HandleRegistryEntryIterable(_ChainedIterable[_HandleRegistryEntry]):
    def from_app(self, app: str) -> t.Self:
        return self.filter(lambda entry: entry.from_app == app)

    def with_dtype(self, dtype: str) -> t.Self:
        return self.filter(lambda entry: entry.dtype == dtype)

    def with_metadata(self, metadata: dict[str, str]) -> t.Self:
        def cmp(entry: _HandleRegistryEntry) -> bool:
            meta = entry.metadata
            return all(meta.get(key) == val for key, val in metadata.items())

        return self.filter(cmp)


_GLOBAL_REGISTRY: HandleRegistry | None = None


type _ProvidesRegistryFnType[**P] = c_abc.Callable[P, HandleRegistry]
type _ProvidesRegistryFactoryReturnType[**P] = c_abc.Callable[P, Response]
type _ProvidesRegistryFactoryType[**P] = c_abc.Callable[
    [_ProvidesRegistryFnType[P]], _ProvidesRegistryFactoryReturnType[P]
]


@t.overload
def initializes_registry[**P](
    fn: _ProvidesRegistryFnType[P], /
) -> _ProvidesRegistryFactoryReturnType[P]: ...
@t.overload
def initializes_registry[**P](
    fn: None = ..., /
) -> c_abc.Callable[
    [_ProvidesRegistryFnType[P]], _ProvidesRegistryFactoryReturnType[P]
]: ...
def initializes_registry[**P](
    fn: _ProvidesRegistryFnType[P] | None = None, /
) -> _ProvidesRegistryFactoryType[P] | _ProvidesRegistryFactoryReturnType[P]:
    def _initializes_regisitry(
        f: _ProvidesRegistryFnType[P],
    ) -> _ProvidesRegistryFactoryReturnType[P]:
        def _assign_global_registry(*args: P.args, **kwargs: P.kwargs) -> Response:
            global _GLOBAL_REGISTRY
            if _GLOBAL_REGISTRY is not None:
                return make_response(
                    jsonify(
                        {"error", "A handle registry has already been initialized"}
                    ),
                    409,
                )
            _GLOBAL_REGISTRY = f(*args, **kwargs)
            return make_response(
                jsonify({"success": "Workflow has been registered"}), 201
            )

        return _assign_global_registry

    if fn is None:
        return _initializes_regisitry
    return _initializes_regisitry(fn)


type _RequiresHandleRegistryFnType[**P, T] = c_abc.Callable[
    t.Concatenate["HandleRegistry", P], T
]
type _RequiresHandleRegistryFactoryReturnType[**P, T] = c_abc.Callable[P, T | Response]
type _RequiresHandleRegistryFactoryType[**P, T] = c_abc.Callable[
    [_RequiresHandleRegistryFnType[P, T]],
    _RequiresHandleRegistryFactoryReturnType[P, T],
]


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
