from core.data_model import DataModel
from core.protocol.data_types import TileData


class CreateRoomData(DataModel):
    room_number: int
    player_name: str


class JoinRoomData(DataModel):
    room_number: int
    player_name: str


class StartGameData(DataModel):
    room_number: int


# --- game moves ---


class PlaceTilesData(DataModel):
    tiles_data: list[TileData]


class ExchangeTilesData(DataModel):
    tiles_data: list[TileData]
