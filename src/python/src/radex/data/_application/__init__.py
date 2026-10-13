from __future__ import annotations

import dataclasses
import logging
import typing as t

from flask import Flask, jsonify, request
from radex.data._application.handle_registry import HandleRegistry, requires_registry
from radex.data._types import ApplicationName, ProcessDescription

if t.TYPE_CHECKING:
    from flask import Response

_LOGGER = logging.Logger(__name__)
app = Flask(__name__)


@app.route("/ping", methods=["GET"])
def heartbeat() -> tuple[str, int]:
    return "pong", 200


@app.route("/init/workflow", methods=["POST"])
def register_workflow() -> tuple[Response, int]:
    spec = request.get_json()
    return jsonify(spec), 200


@app.route("/spec/workflow", methods=["GET"])
@requires_registry
def get_workflow_spec(registry: HandleRegistry) -> tuple[Response, int]:
    return jsonify(registry), 200


@app.route("key/writeable/<appname:string>", methods=["GET"])
@requires_registry
def get_writable_keys(registry: HandleRegistry, appname: str):
    handles = registry.find().from_app(appname)
    # TODO: need to decide to how to convert this so that it typeable in C++


@app.route("/key/readable", methods=["GET"])
@requires_registry
def get_readable_keys(registry: HandleRegistry):
    handles = (
        registry.find()
        .from_app(request.args.get("appname"))
        .with_dtype(request.args.get("dtype"))
        .with_metadata(request.args.get("metadata"))
        .collect_or(None)
    )
    # TODO: need to decide to how to convert this so that it typeable in C++


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
