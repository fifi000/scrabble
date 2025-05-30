from __future__ import annotations
from dataclasses import asdict, dataclass, fields, is_dataclass
import json
from types import UnionType
from typing import Type, TypeVar, Union, get_type_hints, get_args
from pprint import pp


T = TypeVar('T', bound='BaseData')


@dataclass
class BaseData:
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
                    (
                        arg
                        for arg in get_args(field_type)
                        if arg is not type(None) and isinstance(arg, type)
                    ),
                    type(None),
                )

            # standard case
            if (
                isinstance(value, dict)
                and is_dataclass(field_type)
                and issubclass(field_type, BaseData)
            ):
                init_kwargs[field.name] = field_type.from_dict(value)

            # list of dataclasses case
            elif (
                isinstance(value, list)
                and is_dataclass(field_type := get_args(field_type)[0])
                and issubclass(field_type, BaseData)
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


class ClientData:
    @dataclass
    class CreateRoomData(BaseData):
        room_number: int
        player_name: str

    @dataclass
    class JoinRoomData(BaseData):
        room_number: int
        player_name: str

    @dataclass
    class PlaceTilesData(BaseData):
        tile_ids: list[str]
        field_positions: list[tuple[int, int]]


# server data


class ServerData:
    @dataclass
    class PlayerInfo(BaseData):
        name: str
        id: str

    @dataclass
    class NewRoomData(BaseData):
        room_number: int
        player_info: ServerData.PlayerInfo | None = None

    @dataclass
    class JoinRoomData(BaseData):
        room_number: int
        player_infos: list[ServerData.PlayerInfo]

    @dataclass
    class NewPlayerData(BaseData):
        player_info: ServerData.PlayerInfo

    @dataclass
    class NewTiles(BaseData):
        tiles: list[dict]


def show(data: BaseData) -> None:
    print('before')
    pp(data.to_dict())

    print()

    print('after')
    pp(data.from_dict(data.to_dict()))


# data = {
#     'room_number': 1235,
#     'player_info': {'name': 'feefee', 'id': '21dcec45-679d-442e-bd14-144a2d41a676'},
# }
# obj = ServerData.NewRoomData.from_dict(data)

data = {
    'room_number': 1235,
    'player_infos': [
        {'name': 'feefee', 'id': '21dcec45-679d-442e-bd14-144a2d41a676'},
        {'name': 'feefee', 'id': '21dcec45-679d-442e-bd14-144a2d41a676'},
        {'name': 'feefee', 'id': '21dcec45-679d-442e-bd14-144a2d41a676'},
        {'name': 'feefee', 'id': '21dcec45-679d-442e-bd14-144a2d41a676'},
    ],
}
obj = ServerData.JoinRoomData.from_dict(data)

pp(obj)
# show(person)
