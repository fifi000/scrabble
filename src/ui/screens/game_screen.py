from uuid import UUID

from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Button
from textual.containers import Vertical, Container

from core.game_logic.board import ROW_COUNT, COLUMN_COUNT
from core.game_logic.game import Game
from core.game_logic.player import Player
from ui.widgets.move_buttons import MoveButtons
from ui.widgets.tile import Tile
from ui.widgets.board import Board
from ui.widgets.field import Field
from ui.widgets.tile_rack import TileRack


class GameScreen(Screen):
    def __init__(self, game: Game, player_id: UUID, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.game = game
        self.player_id = player_id

        self.placed_tiles: list[tuple[Tile, Field]] = []

        # board
        self.board = self._get_board()

        # available letters
        self.tile_rack = TileRack(
            [Tile(tile.symbol, tile.points) for tile in self.player.tiles]
        )

        # move buttons
        self.move_buttons = MoveButtons()

    @property
    def player(self) -> Player:
        return self.game.get_player(self.player_id)

    def _get_board(self) -> Board:
        fields = [
            Field(game_field.type) for row in self.game.board.grid for game_field in row
        ]

        return Board(ROW_COUNT, COLUMN_COUNT, fields)

    def compose(self) -> ComposeResult:
        yield Header(name='Scrabble')

        with Container():
            yield self.board
            with Vertical():
                yield self.tile_rack
                yield self.move_buttons

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
