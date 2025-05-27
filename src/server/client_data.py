from dataclasses import dataclass
from enum import StrEnum

from server.base_data import BaseData


class ClientMessageType(StrEnum):
    JOIN_ROOM = 'join_room'
    START_GAME = 'start_game'
    PLACE_TILES = 'place_tiles'
    CREATE_ROOM = 'create_room'


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
