import logging

from websockets import ServerConnection

from core.game.scrabble_game import GameConfig, ScrabbleGame
from core.protocol import client_data, server_data
from core.protocol.data_types import BoardData, PlayerData
from core.protocol.message_types import ServerMessageType
from server.communication import send_to_player
from server.exception_handler import handle_exception
from server.exceptions import (
    NoActiveConnectionError,
    NoActiveGameError,
    PlayerNotInRoomError,
)
from server.handlers.base_handler import BaseHandler


class GameHandler(BaseHandler):
    @handle_exception
    async def handle_start_game(self, websocket: ServerConnection) -> None:
        room = self.room_manager.find_room_by_connection(websocket)

        if room is None:
            raise NoActiveConnectionError()

        if room.game is not None:
            raise NoActiveGameError(room_number=room.number)

        logging.info(f'Starting game in room {room.number}...')

        players = list(room.get_players())
        room.game = ScrabbleGame(config=GameConfig.default(), players=players)

        room.game.start()

        logging.info(
            f'Game started in room {room.number}, with {len(room.game._players)} players'
        )

        for ws, player in room.get_connected_players():
            await send_to_player(
                ws,
                ServerMessageType.NEW_GAME,
                server_data.NewGameData(
                    player=PlayerData.from_player(player, with_tiles=True),
                    current_player_id=room.game.current_player.id,
                    players=[PlayerData.from_player(p) for p in room.game._players],
                    board=BoardData.from_board(room.game._board),
                ),
            )

    @handle_exception
    async def handle_place_tiles(
        self, websocket: ServerConnection, data: client_data.PlaceTilesData
    ):
        room = self.room_manager.find_room_by_connection(websocket)

        if room is None:
            raise NoActiveConnectionError()

        if room.game is None:
            raise NoActiveGameError(room_number=room.number)

        player = room.find_player_by_connection(websocket)

        if player is None:
            raise PlayerNotInRoomError(room_number=room.number)

        logging.info(f'Player {player.name} is placing tiles in room {room.number}')

        tile_positions = [
            (player.get_tile_by_id(tile_data.id), tile_data.position)
            for tile_data in data.tiles_data
        ]

        assert all(position for tile, position in tile_positions)

        room.game.place_tiles(
            player=player,
            tile_positions=tile_positions,  # type: ignore[asignment]
        )

        for ws, player in room.get_connected_players():
            await send_to_player(
                ws,
                ServerMessageType.NEXT_TURN,
                server_data.NextTurnData(
                    player=PlayerData.from_player(player, with_tiles=True),
                    current_player_id=room.game.current_player.id,
                    players=[PlayerData.from_player(p) for p in room.game._players],
                    board=BoardData.from_board(room.game._board),
                ),
            )

    @handle_exception
    async def handle_exchange_tiles(
        self, websocket: ServerConnection, data: client_data.ExchangeTilesData
    ):
        room = self.room_manager.find_room_by_connection(websocket)

        if room is None:
            raise NoActiveConnectionError()

        if room.game is None:
            raise NoActiveGameError(room_number=room.number)

        player = room.find_player_by_connection(websocket)

        if player is None:
            raise PlayerNotInRoomError(room_number=room.number)

        logging.info(f'Player {player.name} is exchanging tiles in room {room.number}')

        room.game.exchange_tiles(
            player=player,
            tiles=[
                player.get_tile_by_id(tile_data.id) for tile_data in data.tiles_data
            ],
        )

        for ws, player in room.get_connected_players():
            await send_to_player(
                ws,
                ServerMessageType.NEXT_TURN,
                server_data.NextTurnData(
                    player=PlayerData.from_player(player, with_tiles=True),
                    current_player_id=room.game.current_player.id,
                    players=[PlayerData.from_player(p) for p in room.game._players],
                    board=BoardData.from_board(room.game._board),
                ),
            )

    @handle_exception
    async def handle_skip_turn(self, websocket: ServerConnection):
        room = self.room_manager.find_room_by_connection(websocket)

        if room is None:
            raise NoActiveConnectionError()

        if room.game is None:
            raise NoActiveGameError(room_number=room.number)

        player = room.find_player_by_connection(websocket)

        if player is None:
            raise PlayerNotInRoomError(room_number=room.number)

        logging.info(
            f'Player {player.name} is skipping their turn in room {room.number}'
        )

        room.game.skip_turn(player=player)

        for ws, player in room.get_connected_players():
            await send_to_player(
                ws,
                ServerMessageType.NEXT_TURN,
                server_data.NextTurnData(
                    player=PlayerData.from_player(player, with_tiles=True),
                    current_player_id=room.game.current_player.id,
                    players=[PlayerData.from_player(p) for p in room.game._players],
                    board=BoardData.from_board(room.game._board),
                ),
            )
