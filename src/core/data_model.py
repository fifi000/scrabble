from typing import Any, Self

from pydantic import BaseModel


class DataModel(BaseModel):
    @classmethod
    def from_json(cls, json_string: str) -> Self:
        return cls.model_validate_json(json_string)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls.model_validate(data)

    def to_json(self) -> str:
        return self.model_dump_json()

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
