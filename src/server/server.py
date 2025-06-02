import asyncio
import json
import logging
from typing import Any

from websockets.asyncio.server import ServerConnection, serve

from core.protocol import client_data
from core.protocol import server_data
from core.data_model import DataModel
from core.game_logic.enums.language import Language
from core.game_logic.game import Game
from core.game_logic.player import Player
from core.game_logic.position import Position
from core.protocol.data_types import BoardData, PlayerData
from core.protocol.message_data import MessageData
from core.protocol.message_types import (
    ClientMessageType,
    ServerMessageType,
    ServerErrorCode,
)
from server.exception import (
    CouldNotStartGameError,
    InvalidMoveError,
    RoomAlreadyExistsError,
    RoomNotFoundError,
)
from server.player_client import PlayerClient
from server.room import Room
from server.room_manager import RoomManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

room_manager = RoomManager()


# --- room actions ---


def join_room(
    websocket: ServerConnection,
    data: client_data.JoinRoomData,
) -> tuple[Player, Room]:
    logging.info(f'Joining player {data.player_name} to room {data.room_number}')
    player = Player(data.player_name)

    room = room_manager.join_room(data.room_number, PlayerClient(websocket, player))

    logging.info(f'Player {data.player_name} joined room {data.room_number}')

    return player, room


async def handle_create_room(
    websocket: ServerConnection,
    data: client_data.CreateRoomData,
) -> None:
    logging.info(f'Creating room {data.room_number} for player {data.player_name}')

    try:
        room = room_manager.create_room(data.room_number)
    except RoomAlreadyExistsError:
        await send_error(
            websocket=websocket,
            code=ServerErrorCode.ROOM_ALREADY_EXISTS,
            message=f'Room {data.room_number} already exists',
            details={'room_number': data.room_number},
        )
        return

    logging.info(f'Room {data.room_number} created')

    try:
        player, room = join_room(
            websocket,
            client_data.JoinRoomData(
                room_number=data.room_number,
                player_name=data.player_name,
            ),
        )
    except RoomNotFoundError:
        await send_error(
            websocket=websocket,
            code=ServerErrorCode.ROOM_NOT_FOUND,
            message=f'Room {data.room_number} not found',
            details={'room_number': data.room_number},
        )
        return

    await send_to_player(
        websocket,
        ServerMessageType.NEW_ROOM_CREATED,
        server_data.NewRoomData(
            room_number=room.number,
            player=PlayerData.from_player(player),
        ),
    )


async def handle_join_room(
    websocket: ServerConnection,
    data: client_data.JoinRoomData,
) -> None:
    try:
        player, room = join_room(websocket, data)
    except RoomNotFoundError:
        await send_error(
            websocket=websocket,
            code=ServerErrorCode.ROOM_NOT_FOUND,
            message=f'Room {data.room_number} not found',
            details={'room_number': data.room_number},
        )
        return

    await send_to_player(
        websocket,
        ServerMessageType.JOIN_ROOM,
        server_data.JoinRoomData(
            room_number=room.number,
            player=[PlayerData.from_player(p) for p in room.get_players()],
        ),
    )

    await broadcast_to_players(
        room,
        ServerMessageType.NEW_PLAYER,
        server_data.NewPlayerData(
            player=PlayerData.from_player(player),
        ),
        players_to_skip=[player],
    )


# --- game actions ---


async def handle_start_game(websocket: ServerConnection) -> None:
    room = room_manager.find_room_by_connection(websocket)

    if room is None:
        await send_error(
            websocket=websocket,
            code=ServerErrorCode.ROOM_NOT_FOUND,
            message='No room found for given connection',
        )
        return

    if room.game is not None:
        await send_error(
            websocket=websocket,
            code=ServerErrorCode.GAME_ALREADY_STARTED,
            message='Game has already started in this room',
            details={'room_number': room.number},
        )
        return

    logging.info(f'Starting game in room {room.number}...')

    players = list(room.get_players())
    room.game = Game(Language.POLISH, players=players)

    try:
        room.game.start()
    except CouldNotStartGameError:
        await send_error(
            websocket=websocket,
            code=ServerErrorCode.GAME_START_FAILED,
            message='Game could not be started',
            details={'room_number': room.number},
        )
        return

    logging.info(
        f'Game started in room {room.number}, with {len(room.game.players)} players'
    )

    for ws, player in room:
        await send_to_player(
            ws,
            ServerMessageType.NEW_GAME,
            server_data.NewGameData(
                player=PlayerData.from_player(player, with_tiles=True),
                current_player_id=room.game.current_player.id,
                players=[PlayerData.from_player(p) for p in room.game.players],
                board=BoardData.from_board(room.game.board),
            ),
        )


async def handle_place_tiles(
    websocket: ServerConnection,
    data: client_data.PlaceTilesData,
):
    room = room_manager.find_room_by_connection(websocket)

    if room is None:
        await send_error(
            websocket=websocket,
            code=ServerErrorCode.ROOM_NOT_FOUND,
            message='No room found for given connection',
        )
        return

    if room.game is None:
        await send_error(
            websocket=websocket,
            code=ServerErrorCode.GAME_NOT_STARTED,
            message='Game has not started in this room',
            details={'room_number': room.number},
        )
        return

    player = room.find_player_by_connection(websocket)

    if player is None:
        await send_error(
            websocket=websocket,
            code=ServerErrorCode.PLAYER_NOT_FOUND,
            message='Player not found in room',
            details={'room_number': room.number},
        )
        return

    logging.info(f'Player {player.name} is placing tiles in room {room.number}')

    try:
        room.game.place_tiles(
            player,
            data.tile_ids,
            [Position(*position) for position in data.field_positions],
        )
    except InvalidMoveError:
        await send_error(
            websocket=websocket,
            code=ServerErrorCode.INVALID_MOVE,
            message='Invalid move',
            details={'room_number': room.number, 'player_id': player.id},
        )
        return

    for ws, player in room:
        await send_to_player(
            ws,
            ServerMessageType.NEXT_TURN,
            server_data.NextTurnData(
                player=PlayerData.from_player(player, with_tiles=True),
                current_player_id=room.game.current_player.id,
                players=[PlayerData.from_player(p) for p in room.game.players],
                board=BoardData.from_board(room.game.board),
            ),
        )


# --- server --> client communication ---


async def send_error(
    websocket: ServerConnection,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> None:
    await send_to_player(
        websocket=websocket,
        type=ServerMessageType.ERROR,
        data=server_data.ErrorData(code=code, message=message, details=details),
    )


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
                if message.data is None:
                    await send_error(
                        websocket=websocket,
                        code=ServerErrorCode.MISSING_DATA,
                        message=f'Missing data for {message.type} message',
                    )
                else:
                    data = client_data.CreateRoomData.from_dict(message.data)
                    await handle_create_room(websocket, data)

            case ClientMessageType.JOIN_ROOM:
                if message.data is None:
                    await send_error(
                        websocket=websocket,
                        code=ServerErrorCode.MISSING_DATA,
                        message=f'Missing data for {message.type} message',
                    )
                else:
                    data = client_data.JoinRoomData.from_dict(message.data)
                    await handle_join_room(websocket, data)

            case ClientMessageType.START_GAME:
                await handle_start_game(websocket)

            case ClientMessageType.PLACE_TILES:
                if message.data is None:
                    await send_error(
                        websocket=websocket,
                        code=ServerErrorCode.MISSING_DATA,
                        message=f'Missing data for {message.type} message',
                    )
                else:
                    data = client_data.PlaceTilesData.from_dict(message.data)
                    await handle_place_tiles(websocket, data)

            case _:
                await send_error(
                    websocket=websocket,
                    code=ServerErrorCode.INVALID_MESSAGE_TYPE,
                    message=f'Unsupported message type: {message.type!r}',
                )


async def main():
    while True:
        try:
            room_manager.reset()
            async with serve(game_server, 'localhost', 8765) as server:
                await server.serve_forever()
        except Exception as e:
            logging.error(f'Error in server: {e}')
            logging.info('Restarting server...')
            await asyncio.sleep(3)


if __name__ == '__main__':
    asyncio.run(main())
