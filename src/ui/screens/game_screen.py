from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Header

from core.game_logic.enums.field_type import FieldType
from core.game_logic.player import Player
from core.protocol.data_types import BoardData
from ui.widgets.board import Board
from ui.widgets.field import Field
from ui.widgets.tile import Tile
from ui.widgets.tile_rack import TileRack


class GameScreen(Screen):
    def __init__(
        self, player: Player, players: list[Player], board: BoardData, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.player = player
        self.players = players

        self.placed_tiles: list[tuple[Tile, Field]] = []

        self.board = self._get_board(board)

        # available letters
        self.tile_rack = TileRack(
            [Tile(tile.symbol, tile.points) for tile in self.player.tiles]
        )

    def _get_board(self, board: BoardData) -> Board:
        fields = [Field(FieldType(field.type)) for field in board.fields]

        return Board(board.rows, board.columns, fields)

    def compose(self) -> ComposeResult:
        yield Header(name='Scrabble')

        with Container():
            yield self.board
            with Vertical():
                yield self.tile_rack
                with Horizontal():
                    yield Button.success('Submit', id='submit')
                    yield Button.warning('Exchange', id='exchange')
                    yield Button.error('Skip', id='skip')

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
