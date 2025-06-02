import asyncio
from collections.abc import Awaitable
import json
import websockets
from websockets.asyncio.client import ClientConnection
from typing import Any, Callable
from inspect import iscoroutinefunction

from core.protocol.data_types import MessageData


class GameClient:
    def __init__(
        self,
        on_server_message: Callable[[MessageData], Any]
        | Callable[[MessageData], Awaitable[Any]],
    ) -> None:
        self.on_server_message = on_server_message
        self._websocket: ClientConnection | None = None

    @property
    def is_connected(self) -> bool:
        return self._websocket is not None

    async def connect(self, uri: str) -> None:
        self._websocket = await websockets.connect(uri)

        asyncio.create_task(self._listen())

    async def send(self, type: str, data: dict | None = None) -> None:
        assert self._websocket

        message = MessageData(type, data)

        await self._websocket.send(message.to_json())

    async def _listen(self) -> None:
        assert self._websocket

        async for ws_message in self._websocket:
            message = MessageData.from_dict(json.loads(ws_message))

            # await asyncio.sleep(1.5)
            if iscoroutinefunction(self.on_server_message):
                await self.on_server_message(message)
            else:
                self.on_server_message(message)
