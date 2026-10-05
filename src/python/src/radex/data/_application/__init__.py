from __future__ import annotations

import dataclasses
import typing as t

from flask import Flask, jsonify, request
from radex.data._types import ApplicationName, ProcessDescription

if t.TYPE_CHECKING:
    from flask import Response

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
        return jsonify({"error": "workflow already registered"}), 409
    HANDLE_REGISTRY = request.get_json()
    print("Registered:")
    print("-----------")
    print(HANDLE_REGISTRY)
    return jsonify(HANDLE_REGISTRY), 200


@app.route("/init/<string:application_id>/outgoing", methods=["POST"])
def register_outgoing_handles(application_id: str) -> str:
    return f"Process {application_id} is registering outgoing handles"


@app.route("/init/<string:application_id>/incoming", methods=["POST"])
def register_incoming_handles(application_id: str) -> str:
    return f"Process {application_id} is registering incoming handles"
