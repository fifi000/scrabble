import json
from dataclasses import asdict, dataclass
from typing import Type, TypeVar


T = TypeVar('T')


@dataclass
class BaseData:
    @classmethod
    def from_json(cls: Type[T], json_string: str) -> T:
        return cls(**json.loads(json_string))

    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        return cls(**data)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Message(BaseData):
    type: str
    data: dict | None = None
