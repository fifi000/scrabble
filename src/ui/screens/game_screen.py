from textual.app import ComposeResult
from textual.containers import Container, VerticalGroup
from textual.message import Message
from textual.reactive import reactive, var
from textual.screen import Screen
from textual.widgets import Button, Header

from ui.models import BoardModel, PlayerModel
from ui.widgets.board import Board
from ui.widgets.field import Field
from ui.widgets.move_buttons import MoveButtons
from ui.widgets.score_board import ScoreBoard
from ui.widgets.tile import Tile
from ui.widgets.tile_rack import TileRack


class GameScreen(Screen):
    class SubmitTiles(Message):
        def __init__(
            self,
            tile_ids: list[str],
            field_positions: list[tuple[int, int]],
        ) -> None:
            super().__init__()
            self.tile_ids = tile_ids
            self.field_positions = field_positions

    class ExchangeTiles(Message):
        pass

    class SkipRound(Message):
        pass

    player: var[PlayerModel] = var(PlayerModel.empty)
    players: reactive[list[PlayerModel]] = reactive(list)
    current_player_id: var[str] = var(str)

    @property
    def is_my_turn(self) -> bool:
        return self.player.id == self.current_player_id

    def compose(self) -> ComposeResult:
        yield Header(name='Scrabble')

        with Container():
            yield Board()
            with VerticalGroup():
                yield TileRack()
                yield MoveButtons()
                yield ScoreBoard()

    def update_player(self, player_model: PlayerModel) -> None:
        self.player = player_model
        self.query_one(TileRack).update_tiles(self.player.tiles)

    def update_players(self, player_models: list[PlayerModel]) -> None:
        self.players = player_models
        self.mutate_reactive(GameScreen.players)

    def update_board(self, board_model: BoardModel) -> None:
        board = self.query_one(Board)

        board.update(board_model)
        self.placed_tiles = []

    def update_current_player(self, player_id: str) -> None:
        self.current_player_id = player_id
        self.query_one(MoveButtons).disabled = not self.is_my_turn
        self.query_one(ScoreBoard).update_current_player(self.current_player_id)

    def place_tile(self, tile: Tile, field: Field) -> None:
        if field.tile:
            self.remove_tile(field)

        tile.enabled = False
        field.tile = tile
        self.placed_tiles.append(field)

    def remove_tile(self, field: Field) -> None:
        assert field.tile

        field.tile.enabled = True
        self.placed_tiles.remove(field)
        field.tile = None

    def on_board_field_selected(self, message: Board.FieldSelected) -> None:
        tile = self.query_one(TileRack).get_selected()

        if tile is not None:
            self.place_tile(tile, message.field)
        elif message.field.tile is not None:
            self.remove_tile(message.field)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case 'submit':
                assert all(field.tile for field in self.placed_tiles)

                self.post_message(
                    self.SubmitTiles(
                        tile_ids=[
                            field.tile.tile_model.id for field in self.placed_tiles
                        ],
                        field_positions=[field.position for field in self.placed_tiles],
                    )
                )
            case 'exchange':
                pass

            case 'skip':
                pass

            case _:
                raise Exception(f'Unsupported button id {event.button.id!r}')
