from __future__ import annotations

import base64
import json
import typing as t
import urllib.parse

from radex.data._types import HandleResponseType, JsonType, WorkflowSpecType
from radex.handles.handles import IncomingHandle, OutgoingHandle

if t.TYPE_CHECKING:
    from radex.data._application.handles._types import HandleRegistryEntry


_URL_STR_ENCODING: t.Final = "utf-8"


def esacpe_for_url(value: str, /) -> str:
    return urllib.parse.quote(value, safe="", encoding=_URL_STR_ENCODING)


def unesacpe_url_val(val: str, /) -> str:
    return urllib.parse.unquote(val, encoding=_URL_STR_ENCODING)


_SPEC_JSON_ENCODING: t.Final = "utf-8"
_SPEC_B64_BLOB_ENCODING: t.Final = "utf-8"


def encode_spec(spec: WorkflowSpecType, /) -> bytes:
    bytes_ = json.dumps(spec_to_json(spec), separators=(",", ":")).encode(
        _SPEC_JSON_ENCODING
    )
    return base64.b64encode(bytes_)


def decode_spec(bytes_: bytes, /) -> WorkflowSpecType:
    string = base64.b64decode(bytes_).decode(_SPEC_JSON_ENCODING)
    spec = json.loads(string)
    return json_to_spec(spec)


def spec_from_str(string: str, /) -> WorkflowSpecType:
    bytes_ = string.encode(_SPEC_B64_BLOB_ENCODING)
    return decode_spec(bytes_)


def spec_to_str(spec: WorkflowSpecType, /) -> str:
    dump = encode_spec(spec)
    return dump.decode(_SPEC_B64_BLOB_ENCODING)


def spec_to_json(spec: WorkflowSpecType, /) -> JsonType:
    # We know this is true, but we should probably validate has we are changing
    # the the `WorkflowSepcType` in case this changes in future and no longer
    # trivially jsonable
    return t.cast(JsonType, spec)


def json_to_spec(json_: JsonType) -> WorkflowSpecType:
    if not isinstance(json_, dict):
        raise TypeError("Loaded json is not of object type")
    # TODO: parse more here if we care
    return t.cast(WorkflowSpecType, json_)


def handle_to_response(entry: HandleRegistryEntry) -> HandleResponseType:
    # TODO: what more infromation should we put in this response
    return {
        # FIXME: This is not really a uuid (though it will be unique if only
        #        one spec is ever initialized)
        "uuid": f"{entry.from_app}-{entry.name}"
    }


def json_to_handle_response(json_: JsonType, /) -> HandleResponseType:
    if not isinstance(json_, dict):
        raise TypeError("Loaded json is not of obejct type")
    if not "uuid" in json_:
        raise ValueError("Missing `uuid` key from json object")
    # TODO: parse more here if we care
    return t.cast(HandleResponseType, json_)


def response_to_outgoing_handle(res: HandleResponseType) -> OutgoingHandle:
    return OutgoingHandle(res["uuid"])


def response_to_incoming_handle(res: HandleResponseType) -> IncomingHandle:
    return IncomingHandle(res["uuid"])
