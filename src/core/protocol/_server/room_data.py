from abc import ABC

from core.data_model import DataModel
from core.protocol.data_types.player_data import PlayerData
from core.protocol.sessionable import Sessionable


class BaseRoomData(Sessionable, ABC):
    """Base class for room-related data."""

    room_number: int
    session_id: str


class NewRoomData(BaseRoomData):
    """Data model for creating a new room."""

    player: PlayerData


class JoinRoomData(BaseRoomData):
    """Data model for joining an existing room."""

    player: PlayerData
    players: list[PlayerData]


class RejoinRoomData(BaseRoomData):
    """Data model for rejoining a room."""

    players: list[PlayerData]


class PlayerJoinedData(DataModel):
    """Data model for players about player joining a room."""

    player: PlayerData


class PlayerRejoinedData(DataModel):
    """Data model for players about player rejoining a room."""

    player: PlayerData
