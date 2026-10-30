from __future__ import annotations

import collections.abc as c_abc
import functools
import typing as t

from flask import Response, jsonify, make_response

if t.TYPE_CHECKING:
    from radex.data._application.handles.registry import HandleRegistry


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
        @functools.wraps(f)
        def _assign_global_registry(*args: P.args, **kwargs: P.kwargs) -> Response:
            global _GLOBAL_REGISTRY
            if _GLOBAL_REGISTRY is not None:
                return make_response(
                    jsonify(
                        {"error": "A handle registry has already been initialized"}
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
        @functools.wraps(f)
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
