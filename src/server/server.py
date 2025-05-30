import asyncio
import json
import uuid
from uuid import UUID

import logging

from websockets.asyncio.server import ServerConnection, serve

from core.game_logic.enums.language import Language
from core.game_logic.game import Game
from core.game_logic.player import Player
from core.protocol.data_types import MessageData, ClientData, ServerData
from core.protocol.message_types import ClientMessageType, ServerMessageType
from server.connection_manager import ConnectionManager
from server.room import Room


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


# room actions


def join_room(
    websocket: ServerConnection, data: ClientData.JoinRoomData
) -> tuple[Player, Room]:
    logging.info(f'Joining player {data.player_name} to room {data.room_number}')
    player = Player(uuid.uuid4(), data.player_name)

    room = ConnectionManager.join_room(data.room_number, websocket, player)
    logging.info(f'Player {data.player_name} joined room {data.room_number}')

    return player, room


async def handle_create_room(
    websocket: ServerConnection, data: ClientData.CreateRoomData
) -> None:
    logging.info(f'Creating room {data.room_number} for player {data.player_name}')

    room = ConnectionManager.create_room(data.room_number)

    logging.info(f'Room {data.room_number} created')

    player, room = join_room(
        websocket, ClientData.JoinRoomData(data.room_number, data.player_name)
    )

    await websocket.send(
        MessageData(
            ServerMessageType.NEW_ROOM_CREATED,
            ServerData.NewRoomData(
                room.number,
                ServerData.PlayerInfo(
                    player.name,
                    str(player.id),
                ),
            ).to_dict(),
        ).to_json()
    )


async def handle_join_room(
    websocket: ServerConnection, data: ClientData.JoinRoomData
) -> None:
    player, room = join_room(websocket, data)

    players = [p for ws, p in room]

    await websocket.send(
        MessageData(
            ServerMessageType.JOIN_ROOM,
            ServerData.JoinRoomData(
                room.number, [ServerData.PlayerInfo(p.name, str(p.id)) for p in players]
            ).to_dict(),
        ).to_json()
    )

    await broadcast_to_players(
        MessageData(
            ServerMessageType.NEW_PLAYER,
            ServerData.NewPlayerData(
                ServerData.PlayerInfo(player.name, str(player.id))
            ).to_dict(),
        ),
        room,
        player,
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
                ServerData.NewTiles(
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


async def handle_place_letters(
    websocket: ServerConnection, data: ClientData.PlaceTilesData
):
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
            ServerData.NewTiles(
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


async def broadcast_to_players(
    message: MessageData,
    room: Room,
    player_to_skip: Player | None = None,
) -> None:
    for websocket, player in room:
        if player_to_skip and player_to_skip.id == player.id:
            continue
        await websocket.send(message.to_json())


# client entry point


async def game_server(websocket: ServerConnection) -> None:
    async for ws_message in websocket:
        logging.info(f'Received message: {ws_message}')
        message = MessageData.from_dict(json.loads(ws_message))

        match message.type:
            case ClientMessageType.CREATE_ROOM:
                assert message.data
                data = ClientData.CreateRoomData.from_dict(message.data)
                await handle_create_room(websocket, data)

            case ClientMessageType.JOIN_ROOM:
                assert message.data
                data = ClientData.JoinRoomData.from_dict(message.data)
                await handle_join_room(websocket, data)

            case ClientMessageType.START_GAME:
                await handle_start_game(websocket)

            case ClientMessageType.PLACE_TILES:
                assert message.data
                data = ClientData.PlaceTilesData.from_dict(message.data)
                await handle_place_letters(websocket, data)

            case _:
                raise Exception(f'Unsupported value: {message.type!r}')


async def main():
    while True:
        try:
            ConnectionManager.clear()
            async with serve(game_server, 'localhost', 8765) as server:
                await server.serve_forever()
        except Exception as e:
            logging.error(f'Error in server: {e}')
            await asyncio.sleep(3)
            logging.info('Restarting server...')


if __name__ == '__main__':
    asyncio.run(main())
