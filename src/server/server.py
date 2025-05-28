import asyncio
import json
import uuid
from uuid import UUID

from websockets.asyncio.server import ServerConnection, serve

from core.game_logic.enums.language import Language
from core.game_logic.game import Game
from core.game_logic.player import Player
from core.protocol.data_types import (
    MessageData,
    CreateRoomData,
    JoinRoomData,
    NewPlayerData,
    NewTiles,
    PlaceTilesData,
)
from core.protocol.message_types import ClientMessageType, ServerMessageType
from server.connection_manager import ConnectionManager
from server.room import Room


# room actions


async def handle_create_room(websocket: ServerConnection, data: CreateRoomData) -> None:
    room = ConnectionManager.create_room(data.room_number)

    await websocket.send(
        MessageData(
            ServerMessageType.NEW_ROOM_CREATED,
            {'room_number': room.number},
        ).to_json()
    )


async def handle_join_room(websocket: ServerConnection, data: JoinRoomData) -> None:
    player = Player(uuid.uuid4(), data.player_name)

    room = ConnectionManager.join_room(data.room_number, websocket, player)

    await broadcast_to_players(
        MessageData(
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
            MessageData(
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

    assert (player := room.get_player_by_websocket(websocket))

    new_tiles = room.game.place_tiles(
        player, list(map(UUID, data.tile_ids)), data.field_positions
    )

    await broadcast_to_players(
        MessageData(ServerMessageType.TILES_PLACED, data.to_dict()), room
    )

    await websocket.send(
        MessageData(
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


async def broadcast_to_players(message: MessageData, room: Room) -> None:
    for websocket, player in room:
        await websocket.send(message.to_json())


# client entry point


async def game_server(websocket: ServerConnection) -> None:
    async for ws_message in websocket:
        message = MessageData.from_dict(json.loads(ws_message))

        match message.type:
            case ClientMessageType.CREATE_ROOM:
                assert message.data
                data = CreateRoomData.from_dict(message.data)
                await handle_create_room(websocket, data)

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
