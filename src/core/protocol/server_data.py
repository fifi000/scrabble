from core.data_model import DataModel
from core.protocol.data_types import BoardData, PlayerData


class NewRoomData(DataModel):
    room_number: int
    player: PlayerData
    session_id: str


class JoinRoomData(DataModel):
    room_number: int
    player: list[PlayerData]
    session_id: str


class RejoinRoomData(DataModel):
    room_number: int
    player: list[PlayerData]
    session_id: str


class NewPlayerData(DataModel):
    player: PlayerData


class PlayerRejoinData(DataModel):
    player: PlayerData


class RejoinGameData(DataModel):
    player: PlayerData
    current_player_id: str
    players: list[PlayerData]
    board: BoardData


class NewGameData(DataModel):
    player: PlayerData
    current_player_id: str
    players: list[PlayerData]
    board: BoardData


class NextTurnData(DataModel):
    player: PlayerData
    current_player_id: str
    players: list[PlayerData]
    board: BoardData
