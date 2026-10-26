from __future__ import annotations

import base64
import json
import typing as t
import urllib.parse

from radex.data._types import WorkflowSpecType


def esacpe_for_url(value: str, /) -> str:
    return urllib.parse.quote(value, safe="")


_SPEC_JSON_ENCODING: t.Final = "utf-8"
_SPEC_B64_BLOB_ENCODING: t.Final = "utf-8"


def encode_spec(spec: WorkflowSpecType, /) -> bytes:
    bytes_ = json.dumps(spec).encode(_SPEC_JSON_ENCODING)
    return base64.b64encode(bytes_)


def decode_spec(bytes_: bytes, /) -> WorkflowSpecType:
    string = base64.b64decode(bytes_).decode(_SPEC_JSON_ENCODING)
    spec = json.loads(string)
    if not isinstance(spec, dict):
        raise ValueError("Loaded spec did not match a valid shape")
    # TODO: validate more here??
    return t.cast(WorkflowSpecType, spec)


def spec_from_str(string: str, /) -> WorkflowSpecType:
    bytes_ = string.encode(_SPEC_B64_BLOB_ENCODING)
    return decode_spec(bytes_)


def spec_to_str(spec: WorkflowSpecType, /) -> str:
    dump = encode_spec(spec)
    return dump.decode(_SPEC_B64_BLOB_ENCODING)
