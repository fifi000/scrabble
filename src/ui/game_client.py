import asyncio
import json
from collections.abc import Awaitable
from inspect import iscoroutinefunction
from typing import Any, Protocol

import websockets
from websockets.asyncio.client import ClientConnection

from core.protocol.messages import MessageData


class MessageHandler(Protocol):
    def __call__(self, message: MessageData) -> Any | Awaitable[Any]: ...


class GameClient:
    def __init__(self, on_server_message: MessageHandler) -> None:
        self.on_server_message = on_server_message
        self._websocket: ClientConnection | None = None

    def _get_websocket(self) -> ClientConnection:
        if not self._websocket:
            raise RuntimeError(
                f'{GameClient.__name__!r} is not connected. You must call {GameClient.connect.__name__!r} first.'
            )

        return self._websocket

    async def connect(self, uri: str) -> None:
        self._websocket = await websockets.connect(uri)

        asyncio.create_task(self._listen())

    async def send(self, type: str, data: dict | None = None) -> None:
        websocket = self._get_websocket()

        message = MessageData(
            type=type,
            data=data,
        )

        await websocket.send(message.to_json())

    async def _listen(self) -> None:
        websocket = self._get_websocket()

        async for ws_message in websocket:
            message = MessageData.from_dict(json.loads(ws_message))

            # await asyncio.sleep(1.5)
            if iscoroutinefunction(self.on_server_message):
                await self.on_server_message(message)
            else:
                self.on_server_message(message)
