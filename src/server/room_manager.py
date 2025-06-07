from collections.abc import Iterator
from dataclasses import dataclass
from typing import NamedTuple

from websockets.asyncio.server import ServerConnection

from core.game.scrabble_game import ScrabbleGame
from core.game.objects.player import Player
from server.exceptions import (
    DuplicatedConnectionError,
    InvalidPlayerData,
    RoomAlreadyExistsError,
    RoomNotFoundError,
)


class ConnectedPlayer(NamedTuple):
    websocket: ServerConnection
    player: Player


@dataclass
class Room:
    def __init__(self, number: int) -> None:
        self.number = number
        self._connected_players: list[ConnectedPlayer] = []
        self.game: ScrabbleGame | None = None

    def add(self, connected_player: ConnectedPlayer):
        for ws, player in self.get_connected_players():
            # same connection
            if ws.id == connected_player.websocket.id:
                raise DuplicatedConnectionError(
                    player_name=player.name, room_number=self.number
                )
            # different connection, same player id
            elif player.id == connected_player.player.id:
                raise InvalidPlayerData(
                    message=f'Player with ID {connected_player.player.id!r} already exists.',
                    details={
                        'player_id': connected_player.player.id,
                        'room_number': self.number,
                    },
                )
            # different connection, same player name
            elif player.name == connected_player.player.name:
                raise InvalidPlayerData(
                    message=f'Player with name {connected_player.player.name!r} already exists.',
                    details={
                        'player_name': connected_player.player.name,
                        'room_number': self.number,
                    },
                )

        self._connected_players.append(connected_player)

    def find_player_by_connection(self, websocket: ServerConnection) -> Player | None:
        for ws, player in self._connected_players:
            if ws.id == websocket.id:
                return player

        return None

    def get_players(self) -> Iterator[Player]:
        for player_client in self._connected_players:
            yield player_client.player

    def get_websockets(self) -> Iterator[ServerConnection]:
        for player_client in self._connected_players:
            yield player_client.websocket

    def get_connected_players(self) -> Iterator[ConnectedPlayer]:
        for player_client in self._connected_players:
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

    def join_room(self, room_number: int, connected_player: ConnectedPlayer) -> Room:
        try:
            room = self.rooms_mapping[room_number]
        except KeyError as e:
            raise RoomNotFoundError(room_number=room_number) from e

        room.add(connected_player)

        return room

    def get_rooms(self) -> Iterator[Room]:
        for room in self.rooms_mapping.values():
            yield room

    def get_connections(self) -> Iterator[ServerConnection]:
        for room in self.rooms_mapping.values():
            for ws in room.get_websockets():
                yield ws

    def find_room_by_connection(self, websocket: ServerConnection) -> Room | None:
        for room in self.rooms_mapping.values():
            for ws in room.get_websockets():
                if ws.id == websocket.id:
                    return room

        return None
