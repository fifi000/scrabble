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


class ConnectionClosedHandler(Protocol):
    def __call__(self) -> Any | Awaitable[Any]: ...


class GameClient:
    def __init__(
        self,
        on_server_message: MessageHandler,
        on_connection_closed: ConnectionClosedHandler | None = None,
    ) -> None:
        self.on_server_message = on_server_message
        self.on_connection_closed = on_connection_closed
        self._websocket: ClientConnection | None = None
        self._session_id: str | None = None

    @property
    def session_id(self) -> str:
        if self._session_id is None:
            raise RuntimeError(f'{GameClient.__name__!r} session ID is not set.')

        return self._session_id

    @session_id.setter
    def session_id(self, value: str) -> None:
        self._session_id = value

    def _get_websocket(self) -> ClientConnection:
        if not self._websocket:
            raise RuntimeError(
                f'{GameClient.__name__!r} is not connected. You must call {GameClient.connect.__name__!r} first.'
            )

        return self._websocket

    async def connect(self, uri: str) -> None:
        self._websocket = await websockets.connect(uri)

        asyncio.create_task(self._listen())

    async def send(self, type: str, data: dict[str, Any] | None = None) -> None:
        websocket = self._get_websocket()

        message = MessageData(
            type=type,
            data=data,
        )

        await websocket.send(message.to_json())

    async def _listen(self) -> None:
        websocket = self._get_websocket()

        try:
            async for ws_message in websocket:
                message = MessageData.from_dict(json.loads(ws_message))

                if iscoroutinefunction(self.on_server_message):
                    await self.on_server_message(message)
                else:
                    self.on_server_message(message)
        except websockets.exceptions.ConnectionClosedError:
            if self.on_connection_closed is not None:
                if iscoroutinefunction(self.on_connection_closed):
                    await self.on_connection_closed()
                else:
                    self.on_connection_closed()
            else:
                raise
