from dataclasses import dataclass, asdict
from enum import StrEnum
import json
from typing import Type, TypeVar

T = TypeVar('T')


class ClientMessageType(StrEnum):
    JOIN_GAME = 'join_game'
    START_GAME = 'start_game'
    PLACE_TILES = 'place_tiles'


class ServerMessageType(StrEnum):
    NEW_PLAYER = 'new_player'
    GAME_STARTED = 'game_started'
    TILES_PLACED = 'tiles_placed'
    NEW_TILES = 'new_tiles'


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


# client messages


@dataclass
class JoinGameData(BaseData):
    player_name: str


@dataclass
class PlaceTilesData(BaseData):
    tile_ids: list[str]
    field_positions: list[tuple[int, int]]


# server messages


@dataclass
class NewPlayerData(BaseData):
    player_name: str
    player_id: str


@dataclass
class NewTiles(BaseData):
    tiles: list[dict]
