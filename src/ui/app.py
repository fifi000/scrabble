import sys
from collections.abc import Iterable
from typing import assert_never, override

from textual import log, on, work
from textual.app import App, SystemCommand
from textual.driver import Driver
from textual.screen import Screen
from textual.types import CSSPathType

from core.protocol import client_data, server_data
from core.protocol.error_data import ErrorData
from core.protocol.message_data import MessageData
from core.protocol.message_types import ClientMessageType, ServerMessageType
from ui.game_client import GameClient
from ui.models.board_model import BoardModel
from ui.models.player_model import PlayerModel
from ui.screens.dialog_screen import DialogScreen
from ui.screens.error_screen import ErrorScreen
from ui.screens.game_screen import GameScreen
from ui.screens.rejoin_rooms_screen import RejoinRoomsScreen
from ui.screens.room_screen import RoomScreen
from ui.screens.start_menu_screen import StartMenuScreen
from ui.storage_manager import SessionModel, StorageManager


class ScrabbleApp(App[None]):
    CSS_PATH = 'scrabble.tcss'
    TITLE = 'Scrabble'

    def __init__(
        self,
        driver_class: type[Driver] | None = None,
        css_path: CSSPathType | None = None,
        watch_css: bool = False,
        ansi_color: bool = False,
    ):
        super().__init__(
            driver_class=driver_class,
            css_path=css_path,
            watch_css=watch_css,
            ansi_color=ansi_color,
        )
        self._game_client: GameClient | None = None

        storage_manager_class = self._get_storage_manager_class()
        self._storage_manager = storage_manager_class(self, 'feefee_scrabble')

    def _get_storage_manager_class(self) -> type[StorageManager]:
        if self.is_web:
            from ui.storage_managers.web_storage_manager import WebStorageManager

            return WebStorageManager
        elif sys.platform == 'win32':
            from ui.storage_managers.windows_storage_manager import (
                WindowsStorageManager,
            )

            return WindowsStorageManager
        elif sys.platform == 'darwin':
            from ui.storage_managers.mac_os_storage_manager import MacOSStorageManager

            return MacOSStorageManager
        else:
            from ui.storage_managers.linux_storage_manager import LinuxStorageManager

            return LinuxStorageManager

    @property
    def game_client(self) -> GameClient:
        if self._game_client is None:
            raise RuntimeError('Game client is not initialized.')

        return self._game_client

    @property
    def storage_manager(self) -> StorageManager:
        return self._storage_manager

    @work(exclusive=True)
    async def _show_session_id(self) -> None:
        await self.push_screen_wait(
            DialogScreen.prompt(
                'Your session ID',
                input_init_kwargs={'value': self.game_client.session_id},
            )
        )

    @override
    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)

        if isinstance(screen, GameScreen):
            yield SystemCommand(
                'Session ID',
                'Shows session ID of current player',
                self._show_session_id,
            )

    def on_mount(self) -> None:
        self._game_client = GameClient(
            self.handle_server_message,
            self.handle_connection_closed,
        )
        self.push_screen(StartMenuScreen())

    # --- RoomScreen - events ---

    @on(RoomScreen.StartGame)
    async def handle_start_game(self, message: RoomScreen.StartGame):
        await self.game_client.send(
            type=ClientMessageType.START_GAME,
            data=client_data.StartGameData(
                room_number=message.room_number,
                session_id=self.game_client.session_id,
            ).to_dict(),
        )

    # --- StartMenuScreen - events ---

    @on(StartMenuScreen.JoinRoom)
    async def handle_join_room(self, message: StartMenuScreen.JoinRoom) -> None:
        await self.game_client.connect(message.form_info.server_url)

        await self.game_client.send(
            type=ClientMessageType.JOIN_ROOM,
            data=client_data.JoinRoomData(
                room_number=message.form_info.room_number,
                player_name=message.form_info.player_name,
            ).to_dict(),
        )
        self.screen.loading = False

    @on(StartMenuScreen.CreateRoom)
    async def handle_create_room(self, message: StartMenuScreen.CreateRoom) -> None:
        await self.game_client.connect(message.form_info.server_url)

        await self.game_client.send(
            type=ClientMessageType.CREATE_ROOM,
            data=client_data.CreateRoomData(
                room_number=message.form_info.room_number,
                player_name=message.form_info.player_name,
            ).to_dict(),
        )
        self.screen.loading = False

    @work(exclusive=True)
    @on(StartMenuScreen.Rejoin)
    async def handle_rejoin(self, message: StartMenuScreen.Rejoin) -> None:
        sessions = self.storage_manager.read_sessions()
        sessions = [
            info for info in sessions if info.uri == message.form_info.server_url
        ]

        screen = RejoinRoomsScreen()
        screen.update_sessions(sessions)
        session = await self.push_screen_wait(screen)

        if session is not None:
            await self.game_client.connect(session.uri)
            await self.game_client.send(
                type=ClientMessageType.REJOIN,
                data=client_data.RejoinData(
                    room_number=session.room_number,
                    session_id=session.id,
                ).to_dict(),
            )

        self.screen.loading = False

    # --- GameScreen - events ---

    @on(GameScreen.SubmitTiles)
    async def handle_submit_tiles(self, message: GameScreen.SubmitTiles) -> None:
        tiles_data = [model.to_tile_data() for model in message.tile_models]
        await self.game_client.send(
            type=ClientMessageType.PLACE_TILES,
            data=client_data.PlaceTilesData(
                tiles_data=tiles_data, session_id=self.game_client.session_id
            ).to_dict(),
        )

    @on(GameScreen.ExchangeTiles)
    async def handle_exchange_tiles(self, message: GameScreen.ExchangeTiles) -> None:
        tiles_data = [model.to_tile_data() for model in message.tile_models]
        await self.game_client.send(
            type=ClientMessageType.EXCHANGE_TILES,
            data=client_data.ExchangeTilesData(
                tiles_data=tiles_data, session_id=self.game_client.session_id
            ).to_dict(),
        )

    @on(GameScreen.SkipTurn)
    async def handle_skip_turn(self) -> None:
        await self.game_client.send(
            type=ClientMessageType.SKIP_TURN,
            data=client_data.SkipTurnData(
                session_id=self.game_client.session_id
            ).to_dict(),
        )

    # --- handlers ---

    @work(exclusive=True)
    async def handle_server_new_room(self, data: server_data.NewRoomData) -> None:
        self.storage_manager.add_session(
            SessionModel(
                id=data.session_id,
                room_number=data.room_number,
                player_name=data.player.name,
                uri=self.game_client.uri or '',
            )
        )

        self.game_client.session_id = data.session_id
        screen = RoomScreen(data.room_number, [data.player.name])
        await self.switch_screen(screen)

    @work(exclusive=True)
    async def handle_server_join_room(self, data: server_data.JoinRoomData) -> None:
        self.storage_manager.add_session(
            SessionModel(
                id=data.session_id,
                room_number=data.room_number,
                player_name=data.player.name,
                uri=self.game_client.uri or '',
            )
        )

        self.game_client.session_id = data.session_id
        screen = RoomScreen(data.room_number, [info.name for info in data.players])
        await self.switch_screen(screen)

    @work(exclusive=True)
    async def handle_server_rejoin_room(self, data: server_data.RejoinRoomData) -> None:
        self.game_client.session_id = data.session_id
        screen = RoomScreen(data.room_number, [info.name for info in data.players])
        await self.switch_screen(screen)

    def handle_server_new_player(self, data: server_data.PlayerJoinedData) -> None:
        assert isinstance(self.screen, RoomScreen)
        self.screen.add_player(data.player.name)

    @work(exclusive=True)
    async def handle_server_new_game(self, data: server_data.NewGameData) -> None:
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
        screen.loading = False

    @work(exclusive=True)
    async def handle_server_rejoin_game(self, data: server_data.RejoinGameData) -> None:
        self.game_client.session_id = data.session_id
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
        screen.loading = False

    @work(exclusive=True)
    async def handle_server_next_turn(self, data: server_data.NextTurnData) -> None:
        assert isinstance(self.screen, GameScreen)

        self.screen.update_player(PlayerModel.from_player_data(data.player))
        self.screen.update_players(
            [PlayerModel.from_player_data(player) for player in data.players]
        )
        self.screen.update_board(BoardModel.form_board_data(data.board))
        self.screen.update_current_player(data.current_player_id)

    @work(exclusive=True)
    async def handle_server_error_message(self, data: ErrorData) -> None:
        self.screen.loading = False
        await self.push_screen_wait(ErrorScreen(data.to_dict()))

    @work(exclusive=True)
    async def handle_connection_closed(self) -> None:
        self.push_screen(StartMenuScreen())

    @work(exclusive=True)
    async def handle_server_message(self, message: MessageData) -> None:
        print(f'Received server message: {message.type}')

        try:
            message_type = ServerMessageType(message.type)
        except ValueError:
            log.error(f'Unsupported message type: {message.type}')
            self.handle_server_error_message(message)
            raise RuntimeError(f'Unsupported message type: {message.type!r}')

        match message_type:
            case ServerMessageType.NEW_ROOM_CREATED:
                assert message.data
                data = server_data.NewRoomData.from_dict(message.data)
                print(f'Processing new room: {data.room_number}')
                self.handle_server_new_room(data)

            case ServerMessageType.NEW_PLAYER:
                assert message.data
                data = server_data.PlayerJoinedData.from_dict(message.data)
                print(f'Processing new player: {data.player.name}')
                self.handle_server_new_player(data)

            case ServerMessageType.JOIN_ROOM:
                assert message.data
                data = server_data.JoinRoomData.from_dict(message.data)
                print(f'Processing join room: {data.room_number}')
                self.handle_server_join_room(data)

            case ServerMessageType.REJOIN_ROOM:
                assert message.data
                data = server_data.RejoinRoomData.from_dict(message.data)
                print(f'Processing rejoin room: {data.room_number}')
                self.handle_server_rejoin_room(data)

            case ServerMessageType.REJOIN_GAME:
                assert message.data
                data = server_data.RejoinGameData.from_dict(message.data)
                print('Processing rejoin game')
                self.handle_server_rejoin_game(data)

            case ServerMessageType.NEW_GAME:
                assert message.data
                data = server_data.NewGameData.from_dict(message.data)
                print('Processing new game start')
                self.handle_server_new_game(data)

            case ServerMessageType.NEXT_TURN:
                assert message.data
                data = server_data.NextTurnData.from_dict(message.data)
                print(f'Processing next turn, player: {data.current_player_id}')
                self.handle_server_next_turn(data)

            case ServerMessageType.ERROR:
                assert message.data
                data = ErrorData.from_dict(message.data)
                log.error(f'Error from server: {data.message}')
                self.handle_server_error_message(data)

            case ServerMessageType.PLAYER_REJOIN:
                pass

            case _:
                assert_never(message.type)


if __name__ == '__main__':
    ScrabbleApp().run()
