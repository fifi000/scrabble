from textual import work

from core.protocol import server_data
from core.protocol.error_data import ErrorData
from ui.app import ScrabbleApp
from ui.models.board_model import BoardModel
from ui.models.player_model import PlayerModel
from ui.screens.error_screen import ErrorScreen
from ui.screens.game_screen import GameScreen
from ui.screens.room_screen import RoomScreen
from ui.storage_manager import SessionModel


class ServerMessageHandler:
    def __init__(self, app: ScrabbleApp) -> None:
        self.app = app

    @work(exclusive=True)
    async def handle_new_room(self, data: server_data.NewRoomData) -> None:
        self.app.storage_manager.add_session(
            SessionModel(
                id=data.session_id,
                room_number=data.room_number,
                player_name=data.player.name,
                uri=self.app.game_client.uri or '',
            )
        )

        self.app.game_client.session_id = data.session_id
        screen = RoomScreen(data.room_number, [data.player.name])
        await self.app.switch_screen(screen)

    @work(exclusive=True)
    async def handle_join_room(self, data: server_data.JoinRoomData) -> None:
        self.app.storage_manager.add_session(
            SessionModel(
                id=data.session_id,
                room_number=data.room_number,
                player_name=data.player.name,
                uri=self.app.game_client.uri or '',
            )
        )

        self.app.game_client.session_id = data.session_id
        screen = RoomScreen(data.room_number, [info.name for info in data.players])
        await self.app.switch_screen(screen)

    @work(exclusive=True)
    async def handle_rejoin_room(self, data: server_data.RejoinRoomData) -> None:
        self.app.game_client.session_id = data.session_id
        screen = RoomScreen(data.room_number, [info.name for info in data.players])
        await self.app.switch_screen(screen)

    def handle_new_player(self, data: server_data.PlayerJoinedData) -> None:
        assert isinstance(self.app.screen, RoomScreen)
        self.app.screen.add_player(data.player.name)

    @work(exclusive=True)
    async def handle_new_game(self, data: server_data.NewGameData) -> None:
        screen = GameScreen()
        screen.loading = True
        await self.app.switch_screen(screen)

        assert isinstance(self.app.screen, GameScreen)

        self.app.screen.update_player(PlayerModel.from_player_data(data.player))
        self.app.screen.update_players(
            [PlayerModel.from_player_data(player) for player in data.players]
        )
        self.app.screen.update_board(BoardModel.form_board_data(data.board))
        self.app.screen.update_current_player(data.current_player_id)
        screen.loading = False

    @work(exclusive=True)
    async def handle_rejoin_game(self, data: server_data.RejoinGameData) -> None:
        self.app.game_client.session_id = data.session_id
        screen = GameScreen()
        screen.loading = True
        await self.app.switch_screen(screen)

        assert isinstance(self.app.screen, GameScreen)

        self.app.screen.update_player(PlayerModel.from_player_data(data.player))
        self.app.screen.update_players(
            [PlayerModel.from_player_data(player) for player in data.players]
        )
        self.app.screen.update_board(BoardModel.form_board_data(data.board))
        self.app.screen.update_current_player(data.current_player_id)
        screen.loading = False

    @work(exclusive=True)
    async def handle_next_turn(self, data: server_data.NextTurnData) -> None:
        assert isinstance(self.app.screen, GameScreen)

        self.app.screen.update_player(PlayerModel.from_player_data(data.player))
        self.app.screen.update_players(
            [PlayerModel.from_player_data(player) for player in data.players]
        )
        self.app.screen.update_board(BoardModel.form_board_data(data.board))
        self.app.screen.update_current_player(data.current_player_id)

    @work(exclusive=True)
    async def handle_error_message(self, data: ErrorData) -> None:
        self.app.screen.loading = False
        await self.app.push_screen_wait(ErrorScreen(data.to_dict()))
