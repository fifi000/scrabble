from typing import Any
import uuid
from textual.app import App

from core.game_logic.enums.language import Language
from core.game_logic.game import Game

from core.protocol.message_types import ClientMessageType, ServerMessageType
from core.protocol.data_types import (
    CreateRoomData,
    JoinRoomData,
    MessageData,
    NewRoomData,
)

from ui.game_client import GameClient
from ui.screens.game_screen import GameScreen
from ui.screens.start_menu_screen import StartMenuScreen


class ScrabbleApp(App[None]):
    CSS_PATH = 'scrabble.tcss'
    TITLE = 'Scrabble'

    def __init__(self) -> None:
        self.game_client: GameClient | None = None

    def on_mount(self) -> None:
        self.push_screen(StartMenuScreen())

    # StartMenuScreen - events

    # def on_start_menu_screen_join_room(self, message: StartMenuScreen.JoinRoom) -> None:
    #     self.switch_screen(GameScreen(Game(Language.POLISH), uuid.uuid4()))

    async def on_start_menu_screen_create_room(
        self, message: StartMenuScreen.CreateRoom
    ) -> None:
        self.game_client = GameClient(
            message.form_info.server_url,
            self.handle_server_message,
        )

        await self.game_client.send(
            type=ClientMessageType.CREATE_ROOM,
            data=CreateRoomData(message.form_info.room_number).to_dict(),
        )

    async def handle_new_room(self, data: NewRoomData) -> None:
        assert self.game_client

        await self.game_client.send(
            type=ClientMessageType.JOIN_ROOM,
            data=JoinRoomData(data.room_number, '').to_dict(),
        )

    async def handle_server_message(self, message: MessageData) -> None:
        match message.type:
            case ServerMessageType.NEW_ROOM_CREATED:
                assert message.data
                data = NewRoomData.from_dict(message.data)
                await self.handle_new_room(data)

            case _:
                raise Exception(f'Unsupported value: {message.type!r}')


if __name__ == '__main__':
    ScrabbleApp().run()
