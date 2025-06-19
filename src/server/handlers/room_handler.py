import logging
import uuid

from websockets import ServerConnection

from core.game.objects.player import Player
from core.protocol import client_data, server_data
from core.protocol.data_types import PlayerData
from core.protocol.message_types import ServerMessageType
from server.communication import broadcast_to_players, send_to_player
from server.exception_handler import handle_exception
from server.handlers.base_handler import BaseHandler
from server.room_manager import Room, User


class RoomHandler(BaseHandler):
    def _join_room(
        self, websocket: ServerConnection, data: client_data.JoinRoomData
    ) -> tuple[Player, Room]:
        logging.info(f'Joining player {data.player_name} to room {data.room_number}')
        player = Player(name=data.player_name, id=str(uuid.uuid4()))

        room = self.room_manager.join_room(data.room_number, User(websocket, player))

        logging.info(f'Player {data.player_name} joined room {data.room_number}')

        return player, room

    @handle_exception
    async def handle_create_room(
        self, websocket: ServerConnection, data: client_data.CreateRoomData
    ) -> None:
        logging.info(f'Creating room {data.room_number} for player {data.player_name}')

        room = self.room_manager.create_room(data.room_number)

        logging.info(f'Room {data.room_number} created')

        player, room = self._join_room(
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
                room_number=room.number,
                player=PlayerData.from_player(player),
            ),
        )

    @handle_exception
    async def handle_join_room(
        self, websocket: ServerConnection, data: client_data.JoinRoomData
    ) -> None:
        player, room = self._join_room(websocket, data)

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
