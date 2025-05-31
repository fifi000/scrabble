from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields, is_dataclass
from types import UnionType
from typing import Type, TypeVar, get_args, get_type_hints

T = TypeVar('T', bound='DataModel')


@dataclass
class DataModel:
    @classmethod
    def from_json(cls: Type[T], json_string: str) -> T:
        return cls(**json.loads(json_string))

    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        fieldtypes = get_type_hints(cls)
        init_kwargs = {}

        for field in fields(cls):
            init_kwargs[field.name] = value = data.get(field.name)
            field_type: type = fieldtypes[field.name]

            # optional dataclass case
            if isinstance(field_type, UnionType):
                field_type = next(
                    (arg for arg in get_args(field_type) if arg is not type(None)),
                    None,
                )

                if field_type is None:
                    continue

            # straight forward
            if (
                isinstance(value, dict)
                and is_dataclass(field_type)
                and issubclass(field_type, DataModel)
            ):
                init_kwargs[field.name] = field_type.from_dict(value)
            # list of dataclasses
            elif (
                isinstance(value, list)
                and is_dataclass(field_type := get_args(field_type)[0])
                and issubclass(field_type, DataModel)
            ):
                init_kwargs[field.name] = [
                    field_type.from_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]

        return cls(**init_kwargs)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return asdict(self)
