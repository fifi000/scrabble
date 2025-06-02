from collections.abc import Iterable
from websockets.asyncio.server import ServerConnection

from core.game_logic.player import Player
from server.player_client import PlayerClient
from server.room import Room


class RoomManager:
    def __init__(self) -> None:
        self._rooms: dict[int, Room] = {}

    def reset(self) -> None:
        self._rooms.clear()

    def create_room(self, room_number: int) -> Room:
        assert room_number not in self._rooms

        return self._rooms.setdefault(room_number, Room(room_number))

    def join_room(
        self,
        room_number: int,
        websocket: ServerConnection,
        player: Player,
    ) -> Room:
        assert (room := self._rooms.get(room_number))

        room.add(PlayerClient(websocket, player))

        return room

    def get_rooms(self) -> Iterable[Room]:
        for room in self._rooms.values():
            yield room

    def get_room_by_connection(self, websocket: ServerConnection) -> Room | None:
        for room in self._rooms.values():
            for ws, player in room:
                if ws.id == websocket.id:
                    return room

        return None
