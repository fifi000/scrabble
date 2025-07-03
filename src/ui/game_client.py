import asyncio
import inspect
import json
from collections.abc import Awaitable
from typing import Any, Protocol

import websockets
from websockets.asyncio.client import ClientConnection

from core.protocol.message_data import MessageData


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
        self._uri: str | None = None
        self._session_id: str | None = None

    @property
    def session_id(self) -> str:
        if self._session_id is None:
            raise RuntimeError(f'{GameClient.__name__!r} session ID is not set.')

        return self._session_id

    @session_id.setter
    def session_id(self, value: str) -> None:
        self._session_id = value

    @property
    def websocket(self) -> ClientConnection:
        if self._websocket is None:
            raise RuntimeError(
                f'{GameClient.__name__!r} is not connected. You must call {GameClient.connect.__name__!r} first.'
            )

        return self._websocket

    @property
    def uri(self) -> str | None:
        return self._uri

    async def connect(self, uri: str) -> None:
        self._websocket = await websockets.connect(uri)
        self._uri = uri

        asyncio.create_task(self._listen())

    async def send(self, type: str, data: dict[str, Any] | None = None) -> None:
        message = MessageData(type=type, data=data)

        await self.websocket.send(message.to_json())

    async def _listen(self) -> None:
        try:
            async for ws_message in self.websocket:
                message = MessageData.from_dict(json.loads(ws_message))

                if inspect.isawaitable(self.on_server_message):
                    await self.on_server_message(message)
                else:
                    self.on_server_message(message)
        except websockets.exceptions.ConnectionClosedError:
            if self.on_connection_closed is None:
                raise

            if inspect.isawaitable(self.on_connection_closed):
                await self.on_connection_closed()
            else:
                self.on_connection_closed()
