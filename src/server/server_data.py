from dataclasses import dataclass
from enum import StrEnum

from server.base_data import BaseData


class ServerMessageType(StrEnum):
    NEW_ROOM_CREATED = 'new_room_created'
    NEW_PLAYER = 'new_player'
    GAME_STARTED = 'game_started'
    TILES_PLACED = 'tiles_placed'
    NEW_TILES = 'new_tiles'


@dataclass
class NewPlayerData(BaseData):
    player_name: str
    player_id: str


@dataclass
class NewTiles(BaseData):
    tiles: list[dict]
