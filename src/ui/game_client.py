import asyncio
import json
import websockets
from websockets.asyncio.client import ClientConnection
from typing import Callable

from core.protocol.data_types import MessageData


class GameClient:
    def __init__(
        self,
        on_server_message: Callable[[MessageData], None],
    ) -> None:
        self.on_server_message = on_server_message
        self._websocket: ClientConnection | None = None

    @property
    def is_connected(self) -> bool:
        return self._websocket is not None

    async def connect(self, uri: str) -> None:
        self._websocket = await websockets.connect(uri)

        asyncio.create_task(self._listen())

    async def send(self, type: str, data: dict) -> None:
        assert self._websocket

        message = json.dumps({'type': type, 'data': data})
        await self._websocket.send(message)

    async def _listen(self) -> None:
        assert self._websocket

        async for ws_message in self._websocket:
            message = MessageData.from_dict(json.loads(ws_message))

            self.on_server_message(message)
