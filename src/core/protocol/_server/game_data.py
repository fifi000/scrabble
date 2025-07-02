from abc import ABC
from core.data_model import DataModel
from core.protocol.data_types.board_data import BoardData
from core.protocol.data_types.player_data import PlayerData
from core.protocol.sessionable import Sessionable


class BaseGameStateData(DataModel, ABC):
    """Base class for game state data."""

    player: PlayerData
    current_player_id: str
    players: list[PlayerData]
    board: BoardData


class RejoinGameData(BaseGameStateData, Sessionable):
    """Data model for rejoining a game state after a disconnection."""


class NewGameData(BaseGameStateData):
    """Data model for a new game state after starting a game."""


class NextTurnData(BaseGameStateData):
    """Data model for the next turn in the game."""
