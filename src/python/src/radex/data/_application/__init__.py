from __future__ import annotations

import dataclasses
import json
import logging
import typing as t

from flask import Flask, jsonify, make_response, request

from radex.data._application.handles.metadata import Metadata
from radex.data._application.handles.registry import HandleRegistry
from radex.data._application.middleware.handles import (
    initializes_registry,
    requires_registry,
)
from radex.data._types import ApplicationName, ProcessDescription, WorkflowSpecType
from radex.data._utils import parse

if t.TYPE_CHECKING:
    from flask import Response

_LOGGER = logging.Logger(__name__)

# TODO: make this dynamic
_LOGGER.setLevel(logging.DEBUG)

app = Flask(__name__)


@app.route("/ping", methods=["GET"])
def heartbeat() -> Response:
    return make_response("pong", 200)


@app.route("/init/workflow", methods=["POST"])
@initializes_registry
def register_workflow() -> HandleRegistry:
    spec = parse.json_to_spec(request.get_json())
    _LOGGER.debug("Initializing with spec `%s`", json.dumps(spec))
    return HandleRegistry.from_spec(spec)


@app.route("/spec/workflow", methods=["GET"])
@requires_registry
def get_workflow_spec(registry: HandleRegistry) -> Response:
    return make_response(jsonify(registry), 200)


@app.route("/key/writeable/<string:appname>", methods=["GET"])
@requires_registry
def get_writable_keys(registry: HandleRegistry, appname: str) -> Response:
    handles = (
        registry.find()
        .from_origin(appname)
        .with_dtype.if_not_none(request.args.get("dtype"))
        .with_metadata.from_value(Metadata.from_query_string)
        .if_not_none(request.args.get("metadata"))
        .map(parse.handle_to_response)
        .collect()
    )

    # TODO: need to decide to how to convert this so that it typeable in C++
    return make_response(jsonify(handles), 200)


@app.route("/key/readable", methods=["GET"])
@requires_registry
def get_readable_keys(registry: HandleRegistry) -> Response:
    handles = (
        registry.find()
        .from_origin.if_not_none(request.args.get("origin"))
        .with_dtype.if_not_none(request.args.get("dtype"))
        .with_metadata.from_value(Metadata.from_query_string)
        .if_not_none(request.args.get("metadata"))
        .map(parse.handle_to_response)
        .collect()
    )

    # TODO: need to decide to how to convert this so that it typeable in C++
    return make_response(jsonify(handles), 200)


# TODO: We only really care about

# 1) Getting all of the keys that an app can write to and
# 2) Getting all of the keys that can be read from matching on some subset of
#    metadata

# Back of the envelope math says this is simply two routes (get keys writeable
# and search all keys readable), and in theory that is what is being prototyped
# above. If multiple processes claim to be the same app, with the same name,
# give them both the writeable key set, that is a user issue. We should log
# PIDs in some output file with this happens for easier debugging on the user's
# end.
