from websockets.asyncio.server import ServerConnection

from core.game_logic.player import Player
from server.player_client import PlayerClient
from server.room import Room


class ConnectionManager:
    _rooms: dict[int, Room] = {}

    @staticmethod
    def clear() -> None:
        ConnectionManager._rooms.clear()

    @staticmethod
    def create_room(room_number: int) -> Room:
        assert room_number not in ConnectionManager._rooms

        return ConnectionManager._rooms.setdefault(room_number, Room(room_number))

    @staticmethod
    def join_room(
        room_number: int,
        websocket: ServerConnection,
        player: Player,
    ) -> Room:
        assert (room := ConnectionManager._rooms.get(room_number))

        room.add(PlayerClient(websocket, player))

        return room

    @staticmethod
    def get_room_by_connection(websocket: ServerConnection) -> Room | None:
        for room in ConnectionManager._rooms.values():
            for ws, player in room:
                if ws.id == websocket.id:
                    return room

        return None
