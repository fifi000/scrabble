from collections.abc import Iterable
from websockets.asyncio.server import ServerConnection

from core.game_logic.player import Player
from server.exception import RoomAlreadyExistsError, RoomNotFoundError
from server.player_client import PlayerClient
from server.room import Room


class RoomManager:
    def __init__(self) -> None:
        self.rooms_mapping: dict[int, Room] = {}

    def reset(self) -> None:
        self.rooms_mapping.clear()

    def create_room(self, room_number: int) -> Room:
        if room_number in self.rooms_mapping.keys():
            raise RoomAlreadyExistsError(room_number=room_number)

        room = Room(room_number)

        self.rooms_mapping[room_number] = room

        return room

    def join_room(self, room_number: int, player_client: PlayerClient) -> Room:
        try:
            room = self.rooms_mapping[room_number]
        except KeyError as e:
            raise RoomNotFoundError(room_number=room_number) from e

        room.add(player_client)

        return room

    def get_rooms(self) -> Iterable[Room]:
        for room in self.rooms_mapping.values():
            yield room

    def get_connections(self) -> Iterable[ServerConnection]:
        for room in self.rooms_mapping.values():
            for ws in room.get_websockets():
                yield ws

    def find_room_by_connection(self, websocket: ServerConnection) -> Room | None:
        for room in self.rooms_mapping.values():
            for ws in room.get_websockets():
                if ws.id == websocket.id:
                    return room

        return None
