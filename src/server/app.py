import asyncio
import json
import logging
import logging.config
from dataclasses import dataclass
from pathlib import Path

from websockets import ConnectionClosedError
from websockets.asyncio.server import ServerConnection, serve

from core.protocol import client_data
from core.protocol.error_codes import ErrorCode
from core.protocol.message_types import (
    ClientMessageType,
)
from core.protocol.message_data import MessageData
from server.communication import send_error
from server.handlers.game_handler import GameHandler
from server.handlers.room_handler import RoomHandler
from server.room_manager import RoomManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


@dataclass
class ServerConfig:
    host: str = '0.0.0.0'
    port: int = 8765
    log_level: str = 'INFO'
    restart_delay: float = 3
    log_format: str = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    log_file: str | None = None
    enable_websocket_logging: bool = False


def setup_logging(config: ServerConfig) -> None:
    """Configure logging for the server."""
    handlers = ['console']

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {'format': config.log_format, 'datefmt': '%Y-%m-%d %H:%M:%S'},
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s - %(funcName)s()',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': config.log_level,
                'formatter': 'standard',
                'stream': 'ext://sys.stdout',
            }
        },
        'loggers': {
            'server': {
                'level': config.log_level,
                'handlers': handlers,
                'propagate': False,
            },
            'core': {
                'level': config.log_level,
                'handlers': handlers,
                'propagate': False,
            },
        },
        'root': {'level': 'WARNING', 'handlers': handlers},
    }

    # Add file handler if specified
    if config.log_file:
        logging_config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': config.log_level,
            'formatter': 'detailed',
            'filename': config.log_file,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        }
        handlers.append('file')
        logging_config['loggers']['server']['handlers'] = handlers
        logging_config['loggers']['core']['handlers'] = handlers

    # Configure websocket logging
    if not config.enable_websocket_logging:
        logging_config['loggers']['websockets'] = {
            'level': 'WARNING',
            'handlers': handlers,
            'propagate': False,
        }

    logging.config.dictConfig(logging_config)


class GameServer:
    def __init__(self, *, config: ServerConfig | None = None) -> None:
        self.config = config or ServerConfig()

        self.logger = logging.getLogger('server.GameServer')
        self.room_manager = RoomManager()
        self.game_handler = GameHandler(self.room_manager)
        self.room_handler = RoomHandler(self.room_manager, self.game_handler)

        self.logger.info(
            f'Game server initialized - Host: {self.config.host}, Port: {self.config.port}'
        )

    async def run(self) -> None:
        self.logger.info(f'Starting server on {self.config.host}:{self.config.port}')

        try:
            async with serve(
                handler=self.handler, host=self.config.host, port=self.config.port
            ) as server:
                self.logger.info('Server started successfully')
                await server.serve_forever()
        except Exception as e:
            self.logger.error(f'Failed to start server: {e}', exc_info=True)
            raise

    async def handler(self, websocket: ServerConnection) -> None:
        client_info = f'{websocket.remote_address[0]}:{websocket.remote_address[1]}'
        self.logger.info(f'New connection from {client_info}')

        try:
            async for ws_message in websocket:
                self.logger.debug(f'Received message from {client_info}: {ws_message}')

                message_data = MessageData.from_dict(json.loads(ws_message))
                await self.message_router(websocket, message_data)
        except ConnectionClosedError as e:
            self.logger.warning(
                f'Connection closed by {client_info}: {e.reason} ({e.code})'
            )
        finally:
            self.logger.info(f'Connection closed: {client_info}')
            await websocket.close()

    async def message_router(
        self, websocket: ServerConnection, message: MessageData
    ) -> None:
        client_info = f'{websocket.remote_address[0]}:{websocket.remote_address[1]}'
        self.logger.debug(f'Routing message type {message.type} from {client_info}')

        match message.type:
            case ClientMessageType.CREATE_ROOM:
                assert message.data
                data = client_data.CreateRoomData.from_dict(message.data)
                await self.room_handler.handle_create_room(websocket, data)

            case ClientMessageType.JOIN_ROOM:
                assert message.data
                data = client_data.JoinRoomData.from_dict(message.data)
                await self.room_handler.handle_join_room(websocket, data)

            case ClientMessageType.START_GAME:
                assert message.data
                data = client_data.StartGameData.from_dict(message.data)
                await self.game_handler.handle_start_game(websocket, data)

            case ClientMessageType.PLACE_TILES:
                assert message.data
                data = client_data.PlaceTilesData.from_dict(message.data)
                await self.game_handler.handle_place_tiles(websocket, data)

            case ClientMessageType.EXCHANGE_TILES:
                assert message.data
                data = client_data.ExchangeTilesData.from_dict(message.data)
                await self.game_handler.handle_exchange_tiles(websocket, data)

            case ClientMessageType.SKIP_TURN:
                assert message.data
                data = client_data.SkipTurnData.from_dict(message.data)
                await self.game_handler.handle_skip_turn(websocket, data)

            case ClientMessageType.REJOIN:
                assert message.data
                data = client_data.RejoinData.from_dict(message.data)
                await self.room_handler.handle_rejoin_room(websocket, data)

            case _:
                await send_error(
                    websocket=websocket,
                    code=ErrorCode.INVALID_MESSAGE_TYPE,
                    message=f'Unsupported message type: {message.type!r}',
                )


async def main():
    config = ServerConfig(
        log_level='DEBUG',
        log_file='logs/server.log',
        enable_websocket_logging=False,
    )

    # Ensure log directory exists
    if config.log_file:
        Path(config.log_file).parent.mkdir(parents=True, exist_ok=True)

    server = GameServer(config=config)

    try:
        await server.run()
    except KeyboardInterrupt:
        logging.getLogger('server').info('Server shutdown requested')
        raise
    except Exception as e:
        logging.getLogger('server').error(f'Server crashed: {e}', exc_info=True)
        raise


if __name__ == '__main__':
    asyncio.run(main())
