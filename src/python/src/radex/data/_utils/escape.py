from __future__ import annotations

import requests.utils


def url(value: str, /) -> str:
    return requests.url.quote(value)
