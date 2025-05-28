from dataclasses import asdict, dataclass
import json
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
class MessageData(BaseData):
    type: str
    data: dict | None = None


# client data


@dataclass
class CreateRoomData(BaseData):
    room_number: int


@dataclass
class JoinRoomData(BaseData):
    room_number: int
    player_name: str


@dataclass
class PlaceTilesData(BaseData):
    tile_ids: list[str]
    field_positions: list[tuple[int, int]]


# server data


@dataclass
class NewRoomData(BaseData):
    room_number: int


@dataclass
class NewPlayerData(BaseData):
    player_name: str
    player_id: str


@dataclass
class NewTiles(BaseData):
    tiles: list[dict]
