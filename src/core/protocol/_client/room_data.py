from core.data_model import DataModel
from core.protocol.sessionable import Sessionable


class CreateRoomData(DataModel):
    """Data model for creating a room."""

    room_number: int
    player_name: str


class JoinRoomData(DataModel):
    """Data model for joining a room."""

    room_number: int
    player_name: str


class RejoinData(Sessionable, DataModel):
    """Data model for rejoining a room."""

    room_number: int


class StartGameData(Sessionable, DataModel):
    """Data model for starting a game."""

    room_number: int
