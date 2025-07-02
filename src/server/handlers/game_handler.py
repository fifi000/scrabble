import logging

from websockets import ServerConnection

from core.protocol import client_data, server_data
from core.game.scrabble_game import GameConfig, ScrabbleGame
from core.protocol.data_types.board_data import BoardData
from core.protocol.data_types.player_data import PlayerData
from core.protocol.message_types import ServerMessageType
from server.communication import send_to_player
from server.exception_handler import handle_exception
from server.exceptions import (
    NoActiveConnectionError,
    NoActiveGameError,
    PlayerNotInRoomError,
)
from server.room_manager import RoomManager


class GameHandler:
    def __init__(self, room_manager: RoomManager) -> None:
        self.room_manager = room_manager

    @handle_exception
    async def handle_start_game(
        self, websocket: ServerConnection, data: client_data.StartGameData
    ) -> None:
        room = self.room_manager.find_room(data.session_id)

        if room is None:
            raise NoActiveConnectionError()

        if room.game is not None:
            raise NoActiveGameError(room_number=room.number)

        logging.info(f'Starting game in room {room.number}...')

        players = [user.player for user in room.get_users()]
        room.game = ScrabbleGame(config=GameConfig.default(), players=players)

        room.game.start()

        logging.info(
            f'Game started in room {room.number}, with {len(room.game.players)} players'
        )

        for user in room.get_users():
            await send_to_player(
                user.websocket,
                ServerMessageType.NEW_GAME,
                server_data.NewGameData(
                    player=PlayerData.from_player(user.player, with_tiles=True),
                    current_player_id=room.game.current_player.id,
                    players=[PlayerData.from_player(p) for p in room.game.players],
                    board=BoardData.from_board(room.game.board),
                ),
            )

    @handle_exception
    async def handle_place_tiles(
        self, websocket: ServerConnection, data: client_data.PlaceTilesData
    ):
        room = self.room_manager.find_room(data.session_id)

        if room is None:
            raise NoActiveConnectionError()

        if room.game is None:
            raise NoActiveGameError(room_number=room.number)

        user = room.find_user(data.session_id)

        if user is None:
            raise PlayerNotInRoomError(room_number=room.number)

        logging.info(
            f'Player {user.player.name} is placing tiles in room {room.number}'
        )

        tile_positions = [
            (user.player.get_tile_by_id(tile_data.id), tile_data.position)
            for tile_data in data.tiles_data
        ]

        assert all(position for tile, position in tile_positions)

        room.game.place_tiles(
            player=user.player,
            tile_positions=tile_positions,  # type: ignore[asignment]
            blank_symbols=[
                (tile, tile_data.symbol)
                for tile_data in data.tiles_data
                if (tile := user.player.get_tile_by_id(tile_data.id)).is_blank
            ],
        )

        for user in room.get_users():
            await send_to_player(
                user.websocket,
                ServerMessageType.NEXT_TURN,
                server_data.NextTurnData(
                    player=PlayerData.from_player(user.player, with_tiles=True),
                    current_player_id=room.game.current_player.id,
                    players=[PlayerData.from_player(p) for p in room.game.players],
                    board=BoardData.from_board(room.game.board),
                ),
            )

    @handle_exception
    async def handle_exchange_tiles(
        self, websocket: ServerConnection, data: client_data.ExchangeTilesData
    ):
        room = self.room_manager.find_room(data.session_id)

        if room is None:
            raise NoActiveConnectionError()

        if room.game is None:
            raise NoActiveGameError(room_number=room.number)

        user = room.find_user(data.session_id)

        if user is None:
            raise PlayerNotInRoomError(room_number=room.number)

        logging.info(
            f'Player {user.player.name} is exchanging tiles in room {room.number}'
        )

        room.game.exchange_tiles(
            player=user.player,
            tiles=[
                user.player.get_tile_by_id(tile_data.id)
                for tile_data in data.tiles_data
            ],
        )

        for user in room.get_users():
            await send_to_player(
                user.websocket,
                ServerMessageType.NEXT_TURN,
                server_data.NextTurnData(
                    player=PlayerData.from_player(user.player, with_tiles=True),
                    current_player_id=room.game.current_player.id,
                    players=[PlayerData.from_player(p) for p in room.game.players],
                    board=BoardData.from_board(room.game.board),
                ),
            )

    @handle_exception
    async def handle_skip_turn(
        self, websocket: ServerConnection, data: client_data.SkipTurnData
    ):
        room = self.room_manager.find_room(data.session_id)

        if room is None:
            raise NoActiveConnectionError()

        if room.game is None:
            raise NoActiveGameError(room_number=room.number)

        user = room.find_user(data.session_id)

        if user is None:
            raise PlayerNotInRoomError(room_number=room.number)

        logging.info(
            f'Player {user.player.name} is skipping their turn in room {room.number}'
        )

        room.game.skip_turn(player=user.player)

        for user in room.get_users():
            await send_to_player(
                user.websocket,
                ServerMessageType.NEXT_TURN,
                server_data.NextTurnData(
                    player=PlayerData.from_player(user.player, with_tiles=True),
                    current_player_id=room.game.current_player.id,
                    players=[PlayerData.from_player(p) for p in room.game.players],
                    board=BoardData.from_board(room.game.board),
                ),
            )

    @handle_exception
    async def handle_game_rejoin(
        self, websocket: ServerConnection, data: client_data.RejoinData
    ):
        room = self.room_manager.find_room(data.session_id)

        if room is None:
            raise NoActiveConnectionError()

        if room.game is None:
            raise NoActiveGameError(room_number=room.number)

        user = room.find_user(data.session_id)

        if user is None:
            raise PlayerNotInRoomError(room_number=room.number)

        for user in room.get_users():
            await send_to_player(
                user.websocket,
                ServerMessageType.REJOIN_GAME,
                server_data.RejoinGameData(
                    player=PlayerData.from_player(user.player, with_tiles=True),
                    current_player_id=room.game.current_player.id,
                    players=[PlayerData.from_player(p) for p in room.game.players],
                    board=BoardData.from_board(room.game.board),
                    session_id=data.session_id,
                ),
            )
