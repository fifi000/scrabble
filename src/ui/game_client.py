import asyncio
import json
import websockets
from websockets.asyncio.client import ClientConnection
from typing import Awaitable, Callable

from core.protocol.data_types import MessageData


class GameClient:
    def __init__(
        self,
        uri: str,
        on_server_message: Callable[[MessageData], Awaitable[None]],
    ) -> None:
        self.uri = uri
        self.on_server_message = on_server_message

        self._websocket: ClientConnection | None = None

    async def connect(self) -> None:
        self._websocket = await websockets.connect(self.uri)
        asyncio.create_task(self._listen())

    async def send(self, type: str, data: dict) -> None:
        assert self._websocket

        message = json.dumps({'type': type, 'data': data})
        await self._websocket.send(message)

    async def _listen(self) -> None:
        assert self._websocket

        async for ws_message in self._websocket:
            message = MessageData.from_dict(json.loads(ws_message))

            await self.on_server_message(message)
