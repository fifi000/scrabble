from rich.style import Style
from rich.text import Text
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalGroup
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, DataTable, Header

from ui.models import BoardModel, PlayerModel
from ui.widgets.board import Board
from ui.widgets.field import Field
from ui.widgets.tile import Tile
from ui.widgets.tile_rack import TileRack


class GameScreen(Screen):
    class SubmitTiles(Message):
        def __init__(
            self, tile_ids: list[str], field_positions: list[tuple[int, int]]
        ) -> None:
            super().__init__()
            self.tile_ids = tile_ids
            self.field_positions = field_positions

    class ExchangeTiles(Message):
        pass

    class SkipRound(Message):
        pass

    def __init__(
        self,
        player_model: PlayerModel,
        player_models: list[PlayerModel],
        board_model: BoardModel,
        current_player_id: str,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.player_model = player_model
        self.player_models = player_models
        self.current_player_id = current_player_id

        self.placed_tiles: list[Field] = []

        self.board = Board(board_model)

        self.score_board = DataTable(id='score_board')
        self.score_board.border_title = 'Score Board'

        # available letters
        self.tile_rack = TileRack([Tile(tile) for tile in self.player_model.tiles])

    @property
    def is_my_turn(self) -> bool:
        return self.player_model.id == self.current_player_id

    def compose(self) -> ComposeResult:
        yield Header(name='Scrabble')

        with Container():
            yield self.board
            with VerticalGroup():
                yield self.tile_rack
                with Horizontal(id='move_buttons'):
                    yield Button.success(
                        'Submit',
                        id='submit',
                        disabled=(not self.is_my_turn),
                    )
                    yield Button.warning(
                        'Exchange',
                        id='exchange',
                        disabled=(not self.is_my_turn),
                    )
                    yield Button.error(
                        'Skip',
                        id='skip',
                        disabled=(not self.is_my_turn),
                    )

                for player in self.player_models:
                    self.score_board.add_column(
                        Text(
                            text=player.name,
                            style=Style(
                                underline=(player.id == self.current_player_id)
                            ),
                        )
                    )

                players_scores = [player.scores or [] for player in self.player_models]

                for i, row in enumerate(zip(*players_scores), start=1):
                    self.score_board.add_row(*row, label=str(i))

                yield self.score_board

    def update_player(self, player_model: PlayerModel) -> None:
        self.player_model = player_model

    def update_players(self, player_models: list[PlayerModel]) -> None:
        self.player_models = player_models

    def update_board(self, board_model: BoardModel) -> None:
        self.board.update(board_model)
        self.placed_tiles = []

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
        tile = self.tile_rack.get_selected()

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
