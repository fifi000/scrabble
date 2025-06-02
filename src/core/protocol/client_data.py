from core.data_model import DataModel


class CreateRoomData(DataModel):
    room_number: int
    player_name: str


class JoinRoomData(DataModel):
    room_number: int
    player_name: str


class PlaceTilesData(DataModel):
    tile_ids: list[str]
    field_positions: list[tuple[int, int]]
