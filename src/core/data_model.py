from __future__ import annotations
from typing import Any, Type, TypeVar

from pydantic import BaseModel

T = TypeVar('T', bound='DataModel')


class DataModel(BaseModel):
    @classmethod
    def from_json(cls: Type[T], json_string: str) -> T:
        return cls.model_validate_json(json_string)

    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        return cls.model_validate(data)

    def to_json(self) -> str:
        return self.model_dump_json()

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
