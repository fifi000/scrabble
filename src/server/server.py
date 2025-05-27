import asyncio
from collections.abc import Iterator
from dataclasses import dataclass
import json
from typing import NamedTuple
import uuid
from uuid import UUID

from websockets.asyncio.server import ServerConnection, serve

from core.enums.language import Language
from core.game import Game
from core.player import Player
from server.client_data import (
    ClientMessageType,
    CreateRoomData,
    JoinRoomData,
    PlaceTilesData,
)
from server.base_data import Message
from server.server_data import NewTiles, ServerMessageType, NewPlayerData


@dataclass
class PlayerClient(NamedTuple):
    websocket: ServerConnection
    player: Player


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

    def __iter__(self) -> Iterator[PlayerClient]:
        for pc in self._player_clients:
            yield pc


class ConnectionManager:
    _rooms: dict[int, Room] = {}

    @staticmethod
    def create_room(room_number: int) -> None:
        assert room_number not in ConnectionManager._rooms

        ConnectionManager._rooms[room_number] = Room(room_number)

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


# room actions


async def handle_create_room(websocket: ServerConnection, data: CreateRoomData) -> None:
    ConnectionManager.create_room(data.room_number)

    await websocket.send(Message(ServerMessageType.NEW_ROOM_CREATED).to_json())


async def handle_join_room(websocket: ServerConnection, data: JoinRoomData) -> None:
    player = Player(uuid.uuid4(), data.player_name)

    room = ConnectionManager.join_room(data.room_number, websocket, player)

    await broadcast_to_players(
        Message(
            ServerMessageType.NEW_PLAYER,
            NewPlayerData(player.name, str(player.id)).to_dict(),
        ),
        room,
    )


# game actions


async def handle_start_game(websocket: ServerConnection) -> None:
    game = Game(Language.POLISH)
    assert (room := ConnectionManager.get_room_by_connection(websocket))

    room.game = game

    for ws, player in room:
        game.add_player(player)

    game.start()

    for websocket, player in room:
        await websocket.send(
            Message(
                ServerMessageType.GAME_STARTED,
                NewTiles(
                    [
                        {
                            'tile_id': str(tile.id),
                            'symbol': tile.symbol,
                            'points': tile.points,
                        }
                        for tile in player.tiles
                    ]
                ).to_dict(),
            ).to_json()
        )


async def handle_place_letters(websocket: ServerConnection, data: PlaceTilesData):
    assert (room := ConnectionManager.get_room_by_connection(websocket))
    assert room.game

    player = next((player for ws, player in room if ws == websocket))

    new_tiles = room.game.place_tiles(
        player, list(map(UUID, data.tile_ids)), data.field_positions
    )

    await broadcast_to_players(
        Message(ServerMessageType.TILES_PLACED, data.to_dict()), room
    )

    await websocket.send(
        Message(
            ServerMessageType.NEW_TILES,
            NewTiles(
                [
                    {
                        'tile_id': str(tile.id),
                        'symbol': tile.symbol,
                        'points': tile.points,
                    }
                    for tile in new_tiles
                ]
            ).to_dict(),
        ).to_json()
    )


# server broadcasting


async def broadcast_to_players(message: Message, room: Room) -> None:
    for websocket, player in room:
        await websocket.send(message.to_json())


# client entry point


async def game_server(websocket: ServerConnection) -> None:
    async for ws_message in websocket:
        message = Message.from_dict(json.loads(ws_message))

        match message.type:
            case ClientMessageType.JOIN_ROOM:
                assert message.data
                data = JoinRoomData.from_dict(message.data)
                await handle_join_room(websocket, data)

            case ClientMessageType.START_GAME:
                await handle_start_game(websocket)

            case ClientMessageType.PLACE_TILES:
                assert message.data
                data = PlaceTilesData.from_dict(message.data)
                await handle_place_letters(websocket, data)

            case _:
                raise Exception(f'Unsupported value: {message.type!r}')


async def main():
    async with serve(game_server, 'localhost', 8765) as server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
