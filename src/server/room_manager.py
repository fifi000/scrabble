from __future__ import annotations

import uuid
from collections.abc import Iterator
from dataclasses import dataclass

from websockets.asyncio.server import ServerConnection

from core.game.objects.player import Player
from core.game.scrabble_game import ScrabbleGame
from server.exceptions import (
    DuplicatedConnectionError,
    InvalidPlayerData,
    RoomAlreadyExistsError,
    RoomNotFoundError,
)


@dataclass
class User:
    websocket: ServerConnection
    player: Player
    session_id: str
    room: Room


class Room:
    def __init__(self, number: int) -> None:
        self.number = number
        self._users: list[User] = []
        self.game: ScrabbleGame | None = None

    def add(self, new_user: User):
        for user in self.get_users():
            # same connection
            if user.websocket.id == new_user.websocket.id:
                raise DuplicatedConnectionError(
                    player_name=new_user.player.name, room_number=self.number
                )
            # different connection, same player id
            elif user.player.id == new_user.player.id:
                raise InvalidPlayerData(
                    message=f'Player with ID {new_user.player.id!r} already exists.',
                    details={
                        'player_id': new_user.player.id,
                        'room_number': self.number,
                    },
                )
            # different connection, same player name
            elif user.player.name == new_user.player.name:
                raise InvalidPlayerData(
                    message=f'Player with name {new_user.player.name!r} already exists.',
                    details={
                        'player_name': new_user.player.name,
                        'room_number': self.number,
                    },
                )

        self._users.append(new_user)

    def update_user(self, session_id: str, websocket: ServerConnection):
        assert (user := self.find_user(session_id))

        user.websocket = websocket

    def find_user(self, session_id: str) -> User | None:
        for user in self.get_users():
            if user.session_id == session_id:
                return user

        return None

    def get_users(self) -> Iterator[User]:
        for player_client in self._users:
            yield player_client


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

    def join_room(
        self, room_number: int, websocket: ServerConnection, player: Player
    ) -> User:
        try:
            room = self.rooms_mapping[room_number]
        except KeyError as e:
            raise RoomNotFoundError(room_number=room_number) from e

        user = User(websocket, player, str(uuid.uuid4()), room)

        room.add(user)

        return user

    def get_rooms(self) -> Iterator[Room]:
        for room in self.rooms_mapping.values():
            yield room

    def find_room(self, session_id: str) -> Room | None:
        for room in self.get_rooms():
            for user in room.get_users():
                if user.session_id == session_id:
                    return room

        return None
