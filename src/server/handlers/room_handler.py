import logging
import uuid

from websockets import ServerConnection

from core.game.objects.player import Player
from core.protocol import client_data, server_data
from core.protocol.data_types.player_data import PlayerData
from core.protocol.message_types import ServerMessageType
from server.communication import broadcast_to_players, send_to_player
from server.exception_handler import handle_exception
from server.handlers.game_handler import GameHandler
from server.room_manager import RoomManager, User


class RoomHandler:
    def __init__(self, room_manager: RoomManager, game_handler: GameHandler) -> None:
        self.room_manager = room_manager
        self.game_handler = game_handler

    def _join_room(
        self, websocket: ServerConnection, data: client_data.JoinRoomData
    ) -> User:
        logging.info(f'Joining player {data.player_name} to room {data.room_number}')

        player = Player(name=data.player_name, id=str(uuid.uuid4()))
        user = self.room_manager.join_room(data.room_number, websocket, player)

        logging.info(f'Player {data.player_name} joined room {data.room_number}')

        return user

    def _rejoin_room(
        self, websocket: ServerConnection, data: client_data.RejoinData
    ) -> User:
        room = self.room_manager.find_room(data.session_id)
        assert room

        user = room.find_user(data.session_id)
        assert user

        room.update_user(data.session_id, websocket)

        return user

    @handle_exception
    async def handle_create_room(
        self, websocket: ServerConnection, data: client_data.CreateRoomData
    ) -> None:
        logging.info(f'Creating room {data.room_number} for player {data.player_name}')
        _ = self.room_manager.create_room(data.room_number)
        logging.info(f'Room {data.room_number} created')

        user = self._join_room(
            websocket,
            client_data.JoinRoomData(
                room_number=data.room_number,
                player_name=data.player_name,
            ),
        )

        await send_to_player(
            websocket,
            ServerMessageType.NEW_ROOM_CREATED,
            server_data.NewRoomData(
                room_number=user.room.number,
                player=PlayerData.from_player(user.player),
                session_id=user.session_id,
            ),
        )

    @handle_exception
    async def handle_join_room(
        self, websocket: ServerConnection, data: client_data.JoinRoomData
    ) -> None:
        user = self._join_room(websocket, data)

        await send_to_player(
            websocket,
            ServerMessageType.JOIN_ROOM,
            server_data.JoinRoomData(
                room_number=user.room.number,
                player=PlayerData.from_player(user.player),
                players=[
                    PlayerData.from_player(user.player)
                    for user in user.room.get_users()
                ],
                session_id=user.session_id,
            ),
        )

        await broadcast_to_players(
            user.room,
            ServerMessageType.NEW_PLAYER,
            server_data.PlayerJoinedData(
                player=PlayerData.from_player(user.player),
            ),
            players_to_skip=[user.player],
        )

    @handle_exception
    async def handle_rejoin_room(
        self, websocket: ServerConnection, data: client_data.RejoinData
    ) -> None:
        user = self._rejoin_room(websocket, data)

        # there is an active game
        if user.room.game is not None:
            await self.game_handler.handle_game_rejoin(websocket, data)
        # no active game --> only rejoin room
        else:
            await send_to_player(
                websocket,
                ServerMessageType.REJOIN_ROOM,
                server_data.RejoinRoomData(
                    room_number=user.room.number,
                    players=[
                        PlayerData.from_player(user.player)
                        for user in user.room.get_users()
                    ],
                    session_id=user.session_id,
                ),
            )

            await broadcast_to_players(
                user.room,
                ServerMessageType.PLAYER_REJOIN,
                server_data.PlayerRejoinedData(
                    player=PlayerData.from_player(user.player),
                ),
                players_to_skip=[user.player],
            )
