from textual.app import App

from core.protocol.data_types import MessageData, ClientData, ServerData
from core.protocol.message_types import ClientMessageType, ServerMessageType
from ui.game_client import GameClient
from ui.screens.room_screen import RoomScreen
from ui.screens.start_menu_screen import StartMenuScreen


class ScrabbleApp(App[None]):
    CSS_PATH = 'scrabble.tcss'
    TITLE = 'Scrabble'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.game_client = GameClient(
            self.handle_server_message,
        )

    def on_mount(self) -> None:
        self.push_screen(StartMenuScreen())

    # StartMenuScreen - events

    async def on_start_menu_screen_join_room(
        self, message: StartMenuScreen.JoinRoom
    ) -> None:
        await self.game_client.connect(message.form_info.server_url)

        await self.game_client.send(
            type=ClientMessageType.JOIN_ROOM,
            data=ClientData.JoinRoomData(
                message.form_info.room_number,
                message.form_info.player_name,
            ).to_dict(),
        )

    async def on_start_menu_screen_create_room(
        self, message: StartMenuScreen.CreateRoom
    ) -> None:
        await self.game_client.connect(message.form_info.server_url)

        await self.game_client.send(
            type=ClientMessageType.CREATE_ROOM,
            data=ClientData.CreateRoomData(
                message.form_info.room_number,
                message.form_info.player_name,
            ).to_dict(),
        )

    def handle_new_room(self, data: ServerData.NewRoomData) -> None:
        screen = RoomScreen(data.room_number, [data.player_info.name])
        self.switch_screen(screen)

    def handle_join_room(self, data: ServerData.JoinRoomData) -> None:
        screen = RoomScreen(data.room_number, [info.name for info in data.player_infos])
        self.switch_screen(screen)

    def handle_new_player(self, data: ServerData.NewPlayerData) -> None:
        assert isinstance(self.screen, RoomScreen)
        self.screen.add_player(data.player_info.name)

    def handle_server_message(self, message: MessageData) -> None:
        match message.type:
            case ServerMessageType.NEW_ROOM_CREATED:
                assert message.data
                data = ServerData.NewRoomData.from_dict(message.data)
                self.handle_new_room(data)

            case ServerMessageType.NEW_PLAYER:
                assert message.data
                data = ServerData.NewPlayerData.from_dict(message.data)
                self.handle_new_player(data)

            case ServerMessageType.JOIN_ROOM:
                assert message.data
                data = ServerData.JoinRoomData.from_dict(message.data)
                self.handle_join_room(data)

            case _:
                raise Exception(f'Unsupported value: {message.type!r}')


if __name__ == '__main__':
    ScrabbleApp().run()
