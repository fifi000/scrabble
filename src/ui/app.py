import asyncio
import time
from textual import work, log
from textual.app import App
from textual.widgets import Welcome
from textual.screen import Screen

from core.protocol.data_types import ClientData, MessageData, ServerData
from core.protocol.message_types import ClientMessageType, ServerMessageType
from ui.game_client import GameClient
from ui.models import BoardModel, PlayerModel
from ui.screens.game_screen import GameScreen
from ui.screens.message_viewer import MessageViewer
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

    # --- RoomScreen - events ---

    async def on_room_screen_start_game(self, message: RoomScreen.StartGame):
        await self.game_client.send(type=ClientMessageType.START_GAME)

    # --- StartMenuScreen - events ---

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

    # --- GameScreen ---

    async def on_game_screen_submit_tiles(
        self, message: GameScreen.SubmitTiles
    ) -> None:
        await self.game_client.send(
            type=ClientMessageType.PLACE_TILES,
            data=ClientData.PlaceTilesData(
                message.tile_ids,
                message.field_positions,
            ).to_dict(),
        )

    # --- handlers ---

    @work(exclusive=True)
    async def handle_new_room(self, data: ServerData.NewRoomData) -> None:
        screen = RoomScreen(data.room_number, [data.player_info.name])
        await self.switch_screen(screen)

    @work(exclusive=True)
    async def handle_join_room(self, data: ServerData.JoinRoomData) -> None:
        screen = RoomScreen(data.room_number, [info.name for info in data.player_infos])
        await self.switch_screen(screen)

    def handle_new_player(self, data: ServerData.NewPlayerData) -> None:
        assert isinstance(self.screen, RoomScreen)
        self.screen.add_player(data.player_info.name)

    @work(exclusive=True)
    async def handle_new_game(self, data: ServerData.NewGameData) -> None:
        screen = GameScreen()
        screen.loading = True
        await self.switch_screen(screen)

        assert isinstance(self.screen, GameScreen)

        self.screen.update_player(PlayerModel.from_player_data(data.player))
        self.screen.update_players(
            [PlayerModel.from_player_data(player) for player in data.players]
        )
        self.screen.update_board(BoardModel.form_board_data(data.board))
        self.screen.update_current_player(data.current_player_id)

        self.screen.loading = False

    @work(exclusive=True)
    async def handle_next_turn(self, data: ServerData.NextTurnData) -> None:
        assert isinstance(self.screen, GameScreen)

        self.screen.update_player(PlayerModel.from_player_data(data.player))
        self.screen.update_players(
            [PlayerModel.from_player_data(player) for player in data.players]
        )
        self.screen.update_board(BoardModel.form_board_data(data.board))
        self.screen.update_current_player(data.current_player_id)

    @work(exclusive=True)
    async def handle_server_message(self, message: MessageData) -> None:
        print(f'Received server message: {message.type}')

        match message.type:
            case ServerMessageType.NEW_ROOM_CREATED:
                assert message.data
                data = ServerData.NewRoomData.from_dict(message.data)
                print(f'Processing new room: {data.room_number}')
                self.handle_new_room(data)

            case ServerMessageType.NEW_PLAYER:
                assert message.data
                data = ServerData.NewPlayerData.from_dict(message.data)
                print(f'Processing new player: {data.player_info.name}')
                self.handle_new_player(data)

            case ServerMessageType.JOIN_ROOM:
                assert message.data
                data = ServerData.JoinRoomData.from_dict(message.data)
                print(f'Processing join room: {data.room_number}')
                self.handle_join_room(data)

            case ServerMessageType.NEW_GAME:
                assert message.data
                data = ServerData.NewGameData.from_dict(message.data)
                print('Processing new game start')
                self.handle_new_game(data)

            case ServerMessageType.NEXT_TURN:
                assert message.data
                data = ServerData.NextTurnData.from_dict(message.data)
                print(f'Processing next turn, player: {data.current_player_id}')
                self.handle_next_turn(data)

            case _:
                log.error(f'Unsupported message type: {message.type}')
                raise Exception(f'Unsupported value: {message.type!r}')


if __name__ == '__main__':
    ScrabbleApp().run()
