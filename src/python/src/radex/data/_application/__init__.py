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


@app.route("/init/<string:application_id>/outgoing", methods=["POST"])
def register_outgoing_handles(application_id: str) -> str:
    return f"Process {application_id} is registering outgoing handles"


@app.route("/init/<string:application_id>/incoming", methods=["POST"])
def register_incoming_handles(application_id: str) -> str:
    return f"Process {application_id} is registering incoming handles"
