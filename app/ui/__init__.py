from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_JSON_PATH = Path(__file__).parent / "messages.json"


class _Namespace:
    def __init__(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            if key.startswith("_"):
                continue
            if isinstance(value, dict):
                setattr(self, key, _Namespace(value))
            else:
                setattr(self, key, value)

    def __repr__(self) -> str:
        return f"<UI {list(vars(self).keys())}>"


def _load() -> _Namespace:
    with _JSON_PATH.open(encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
    return _Namespace(data)


UI = _load()

__all__ = ["UI"]
