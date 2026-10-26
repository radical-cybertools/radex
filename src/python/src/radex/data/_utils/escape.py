from __future__ import annotations

import urllib.parse


def url(value: str, /) -> str:
    return urllib.parse.quote(value)
