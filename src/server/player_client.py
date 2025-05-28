from typing import NamedTuple

from websockets.asyncio.server import ServerConnection

from core.game_logic.player import Player


class PlayerClient(NamedTuple):
    websocket: ServerConnection
    player: Player
