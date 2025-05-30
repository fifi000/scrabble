import random
from textual.app import ComposeResult
from textual.containers import Container, VerticalGroup, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Header, DataTable

from rich.text import Text
from rich.style import Style

from core.game_logic.enums.field_type import FieldType
from core.protocol.data_types import BoardData, PlayerData
from ui.widgets.board import Board
from ui.widgets.field import Field
from ui.widgets.tile import Tile
from ui.widgets.tile_rack import TileRack


class GameScreen(Screen):
    def __init__(
        self,
        player: PlayerData,
        players: list[PlayerData],
        board: BoardData,
        current_player_id: str,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.player = player
        assert self.player.tiles

        self.players = players
        self.current_player_id = current_player_id

        # for player in self.players:
        #     player.scores = [
        #         random.randint(0, 15),
        #         random.randint(0, 15),
        #         random.randint(0, 15),
        #     ]

        self.placed_tiles: list[tuple[Tile, Field]] = []

        self.board = self._get_board(board)

        self.score_board = DataTable(id='score_board')
        self.score_board.border_title = 'Score Board'

        # available letters
        self.tile_rack = TileRack(
            [Tile(tile.symbol, tile.points) for tile in self.player.tiles]
        )

    @property
    def is_my_turn(self) -> bool:
        return self.player.id == self.current_player_id

    def _get_board(self, board: BoardData) -> Board:
        fields = [Field(FieldType(field.type)) for field in board.fields]

        return Board(board.rows, board.columns, fields)

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

                for player in self.players:
                    self.score_board.add_column(
                        Text(
                            text=player.name,
                            style=Style(
                                underline=(player.id == self.current_player_id)
                            ),
                        )
                    )

                players_scores = [player.scores or [] for player in self.players]

                for i, row in enumerate(zip(*players_scores), start=1):
                    while len(row) < len(self.players):
                        row.append('')
                    self.score_board.add_row(*row, label=str(i))

                yield self.score_board

    def place_tile(self, tile: Tile, field: Field) -> None:
        if field.tile:
            return

        field.tile = tile
        self.tile_rack.remove(tile)

        self.placed_tiles.append((tile, field))

    def submit_word(self) -> None:
        pass

    def on_board_field_selected(self, message: Board.FieldSelected) -> None:
        field = message.field
        tile = self.tile_rack.get_selected()

        if field and tile:
            self.place_tile(tile, field)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case 'submit':
                pass

            case 'exchange':
                pass

            case 'skip':
                pass

            case _:
                raise Exception(f'Unsupported button id {event.button.id!r}')
