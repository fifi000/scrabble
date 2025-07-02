import logging
from typing import Any

from websockets import ServerConnection

from core.data_model import DataModel
from core.game.objects.player import Player
from core.protocol.errors import ErrorData
from core.protocol.message_types import ServerMessageType
from core.protocol.messages import MessageData
from server.room_manager import Room

logger = logging.getLogger(__name__)


async def send_error(
    websocket: ServerConnection,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> None:
    client_info = f'{websocket.remote_address[0]}:{websocket.remote_address[1]}'
    logger.warning(f'Sending error to {client_info}: {code} - {message}')

    await send_to_player(
        websocket=websocket,
        type=ServerMessageType.ERROR,
        data=ErrorData(code=code, message=message, details=details),
    )


async def send_to_player(
    websocket: ServerConnection, type: str, data: DataModel
) -> None:
    client_info = f'{websocket.remote_address[0]}:{websocket.remote_address[1]}'
    logger.debug(f'Sending {type} to {client_info}')

    try:
        await websocket.send(MessageData(type=type, data=data.to_dict()).to_json())
    except Exception as e:
        logger.error(f'Failed to send message to {client_info}: {e}')
        raise


async def broadcast_to_players(
    room: Room,
    type: ServerMessageType,
    data: DataModel,
    *,
    players_to_skip: list[Player] | None = None,
) -> None:
    skip_ids = {player.id for player in players_to_skip or []}

    users = list(room.get_users())

    logger.info(f'Broadcasting {type} to {len(users)} players in room {room.number}')

    for user in users:
        if user.player.id in skip_ids:
            continue

        try:
            await send_to_player(user.websocket, type, data)
        except Exception as e:
            logger.error(f'Failed to broadcast to player {user.player.name}: {e}')
