from __future__ import annotations

import collections.abc as c_abc
import dataclasses
import typing as t


@dataclasses.dataclass(frozen=True)
class Metadata(c_abc.Mapping[str, str]):
    _data: c_abc.Mapping[str, str]

    def __getitem__(self, key: str) -> str:
        try:
            return self._data[key]
        except KeyError:
            raise KeyError(f"Metadata item `{key}` not available")

    def __iter__(self) -> c_abc.Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    @classmethod
    def from_string(cls, string: str) -> t.Self:
        raise NotImplementedError

    def to_string(self) -> str:
        raise NotImplementedError

    @classmethod
    def from_mapping(cls, mapping: c_abc.Mapping[str, str]) -> t.Self:
        return cls(dict(mapping))

    def matches_values(self, other: c_abc.Mapping[str, str]) -> bool:
        return all(self.get(key) == value for key, value in other.items())
