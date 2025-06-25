from core.data_model import DataModel
from core.protocol.data_types import TileData


class CreateRoomData(DataModel):
    room_number: int
    player_name: str


class JoinRoomData(DataModel):
    room_number: int
    player_name: str


class RejoinData(DataModel):
    room_number: int
    session_id: str


class StartGameData(DataModel):
    room_number: int
    session_id: str


# --- game moves ---


class PlaceTilesData(DataModel):
    tiles_data: list[TileData]
    session_id: str


class ExchangeTilesData(DataModel):
    tiles_data: list[TileData]
    session_id: str


class SkipTurnData(DataModel):
    session_id: str
