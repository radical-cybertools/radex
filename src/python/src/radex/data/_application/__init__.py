from __future__ import annotations

import dataclasses
import logging
import typing as t

from flask import Flask, jsonify, request
from radex.data._types import ApplicationName, ProcessDescription

if t.TYPE_CHECKING:
    from flask import Response

_LOGGER = logging.Logger(__name__)
app = Flask(__name__)


# TODO: this registery needs to be updated with what handles have been
#       registrered, declared to be supplied, and have been supplied
HANDLE_REGISTRY: dict[ApplicationName, ProcessDescription] = {}


@app.route("/ping", methods=["GET"])
def heartbeat() -> tuple[str, int]:
    return "pong", 200


@app.route("/init/workflow", methods=["POST"])
def register_workflow() -> tuple[Response, int]:
    global HANDLE_REGISTRY
    if HANDLE_REGISTRY:
        _LOGGER.error("A process attempted to provide a second handle registry")
        return jsonify({"error": "workflow already registered"}), 409
    HANDLE_REGISTRY = request.get_json()
    _LOGGER.info("Registered:", HANDLE_REGISTRY)
    return jsonify(HANDLE_REGISTRY), 200


@app.route("/spec/workflow", methods=["GET"])
def get_workflow_spec() -> tuple[Response, int]:
    if not HANDLE_REGISTRY:
        return jsonify({"error": "Handle registry has not been initialized"}), 404
    return jsonify(HANDLE_REGISTRY), 200


# TODO: We only really care about

# 1) Getting all of the keys that an app can write to and
# 2) Getting all of the keys that can be read from matching on some subset of
#    metadata

# Back of the envelope math says this is simply two routes, in theory don't
# need anything below this comment If multiple processes claim to be the same
# app, with the same name, give them both the writeable key set, that is a user
# issue. We should log PIDs in some output file with this happens for easier
# debugging on the user's end.


@app.route("/init/<string:application_id>/outgoing", methods=["POST"])
def register_outgoing_handles(application_id: str) -> str:
    return f"Process {application_id} is registering outgoing handles"


@app.route("/init/<string:application_id>/incoming", methods=["POST"])
def register_incoming_handles(application_id: str) -> str:
    return f"Process {application_id} is registering incoming handles"
