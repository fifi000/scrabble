import asyncio
import json
import websockets
from websockets.asyncio.client import ClientConnection
from typing import Any, Awaitable, Callable


class GameClient:
    def __init__(
        self, uri: str, on_server_message: Callable[[dict[str, Any]], Awaitable[None]]
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

        async for message in self._websocket:
            event: dict = json.loads(message)
            await self.on_server_message(event)
