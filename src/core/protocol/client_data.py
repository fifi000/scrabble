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


class GameMove(DataModel):
    session_id: str


class PlaceTilesData(GameMove):
    tiles_data: list[TileData]


class ExchangeTilesData(GameMove):
    tiles_data: list[TileData]


class SkipTurnData(GameMove):
    pass
