from core.data_model import DataModel
from core.game.types import Position


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
    tile_positions: list[tuple[str, Position]]


class ExchangeTilesData(DataModel):
    tile_ids: list[str]
