import asyncio
import json
import logging

from websockets.asyncio.server import ServerConnection, serve

from core.game_logic.enums.language import Language
from core.game_logic.game import Game
from core.game_logic.player import Player
from core.game_logic.position import Position
from core.protocol.data_types import (
    BoardData,
    ClientData,
    DataModel,
    MessageData,
    PlayerData,
    ServerData,
)
from core.protocol.message_types import ClientMessageType, ServerMessageType
from server.room_manager import RoomManager
from server.room import Room

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

room_manager = RoomManager()


# --- room actions ---


def join_room(
    websocket: ServerConnection,
    data: ClientData.JoinRoomData,
) -> tuple[Player, Room]:
    logging.info(f'Joining player {data.player_name} to room {data.room_number}')
    player = Player(data.player_name)

    room = room_manager.join_room(data.room_number, websocket, player)
    logging.info(f'Player {data.player_name} joined room {data.room_number}')

    return player, room


async def handle_create_room(
    websocket: ServerConnection,
    data: ClientData.CreateRoomData,
) -> None:
    logging.info(f'Creating room {data.room_number} for player {data.player_name}')

    room = room_manager.create_room(data.room_number)

    logging.info(f'Room {data.room_number} created')

    player, room = join_room(
        websocket,
        ClientData.JoinRoomData(
            room_number=data.room_number,
            player_name=data.player_name,
        ),
    )

    await send_to_player(
        websocket,
        ServerMessageType.NEW_ROOM_CREATED,
        ServerData.NewRoomData(
            room_number=room.number,
            player=PlayerData.from_player(player),
        ),
    )


async def handle_join_room(
    websocket: ServerConnection,
    data: ClientData.JoinRoomData,
) -> None:
    player, room = join_room(websocket, data)

    await send_to_player(
        websocket,
        ServerMessageType.JOIN_ROOM,
        ServerData.JoinRoomData(
            room_number=room.number,
            player=[PlayerData.from_player(p) for p in room.get_players()],
        ),
    )

    await broadcast_to_players(
        room,
        ServerMessageType.NEW_PLAYER,
        ServerData.NewPlayerData(
            player=PlayerData.from_player(player),
        ),
        players_to_skip=[player],
    )


# --- game actions ---


async def handle_start_game(websocket: ServerConnection) -> None:
    assert (room := room_manager.get_room_by_connection(websocket))

    logging.info(f'Starting game in room {room.number}...')

    room.game = Game(Language.POLISH)

    for ws, player in room:
        room.game.add_player(player)

    room.game.start()
    logging.info(
        f'Game started in room {room.number}, with {len(room.game.players)} players'
    )

    for ws, player in room:
        await send_to_player(
            ws,
            ServerMessageType.NEW_GAME,
            ServerData.NewGameData(
                player=PlayerData.from_player(player, with_tiles=True),
                current_player_id=room.game.current_player.id,
                players=[PlayerData.from_player(p) for p in room.game.players],
                board=BoardData.from_board(room.game.board),
            ),
        )


async def handle_place_tiles(
    websocket: ServerConnection,
    data: ClientData.PlaceTilesData,
):
    assert (room := room_manager.get_room_by_connection(websocket))
    assert room.game
    assert (player := room.get_player_by_websocket(websocket))

    logging.info(f'Player {player.name} is placing tiles in room {room.number}')

    room.game.place_tiles(
        player,
        data.tile_ids,
        [Position(*position) for position in data.field_positions],
    )

    for ws, player in room:
        await send_to_player(
            ws,
            ServerMessageType.NEXT_TURN,
            ServerData.NextTurnData(
                player=PlayerData.from_player(player, with_tiles=True),
                current_player_id=room.game.current_player.id,
                players=[PlayerData.from_player(p) for p in room.game.players],
                board=BoardData.from_board(room.game.board),
            ),
        )


# --- server --> client communication ---


async def send_to_player(
    websocket: ServerConnection,
    type: str,
    data: DataModel,
) -> None:
    await websocket.send(
        MessageData(
            type=type,
            data=data.to_dict(),
        ).to_json()
    )


async def broadcast_to_players(
    room: Room,
    type: ServerMessageType,
    data: DataModel,
    players_to_skip: list[Player] = list(),
) -> None:
    skip_ids = {player.id for player in players_to_skip}

    for websocket, player in room:
        if player.id in skip_ids:
            continue
        await send_to_player(websocket, type, data)


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
                await handle_place_tiles(websocket, data)

            case _:
                raise Exception(f'Unsupported value: {message.type!r}')


async def main():
    while True:
        try:
            room_manager.reset()
            async with serve(game_server, 'localhost', 8765) as server:
                await server.serve_forever()
        except Exception as e:
            logging.error(f'Error in server: {e}')
            await asyncio.sleep(3)
            logging.info('Restarting server...')


if __name__ == '__main__':
    asyncio.run(main())
