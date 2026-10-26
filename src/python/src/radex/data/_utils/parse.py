from __future__ import annotations

import json
import urllib.parse

from radex.data._types import WorkflowSpecType


def esacpe_for_url(value: str, /) -> str:
    return urllib.parse.quote(value, safe="")


def spec_from_str(string: str) -> WorkflowSpecType:
    raise NotImplementedError


def spec_to_str(spec: WorkflowSpecType) -> str:
    raise NotImplementedError
