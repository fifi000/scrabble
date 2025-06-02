from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from websockets.asyncio.server import ServerConnection

from core.game_logic.game import Game
from core.game_logic.player import Player
from server.player_client import PlayerClient


@dataclass
class Room:
    def __init__(self, number: int) -> None:
        self.number = number
        self._player_clients: list[PlayerClient] = []
        self.game: Game | None = None

    def add(self, player_client: PlayerClient):
        assert all(
            pc.websocket.id != player_client.websocket.id for pc in self._player_clients
        )
        assert all(
            pc.player.id != player_client.player.id for pc in self._player_clients
        )

        self._player_clients.append(player_client)

    def get_player_by_websocket(self, websocket: ServerConnection) -> Player | None:
        for ws, player in self._player_clients:
            if ws.id == websocket.id:
                return player

        return None

    def get_players(self) -> Iterable[Player]:
        for player_client in self._player_clients:
            yield player_client.player

    def get_websockets(self) -> Iterable[ServerConnection]:
        for player_client in self._player_clients:
            yield player_client.websocket

    def __iter__(self) -> Iterator[PlayerClient]:
        for player_client in self._player_clients:
            yield player_client
