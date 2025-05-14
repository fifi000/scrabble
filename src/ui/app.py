import random
import string
from uuid import UUID

from textual.screen import Screen
from textual.app import App, ComposeResult
from textual.widgets import Header
from textual.widget import Widget
from textual.containers import Horizontal

from core.board import ROW_COUNT, COLUMN_COUNT
from core.enums.language import Language
from core.game import Game as CoreGame
from core.player import Player
from ui.widgets.tile import Tile
from ui.widgets.board import Board
from ui.widgets.field import Field
from ui.widgets.tiles_group import TilesGroup


def get_text() -> str:
    if random.random() > 0.7:
        return random.choice(string.ascii_uppercase) + random.choice(
            ['₀', '₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉']
        )
    else:
        return str()


class Game(Screen):
    CSS_PATH = 'scrabble.tcss'

    def __init__(self, game: CoreGame, player_id: UUID, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.game = game
        self.player_id = player_id

    @property
    def player(self) -> Player:
        return self.game.get_player(self.player_id)

    def _get_board(self) -> Widget:
        fields = [
            Field(game_field) for row in self.game.board.grid for game_field in row
        ]

        return Board(ROW_COUNT, COLUMN_COUNT, fields)

    def compose(self) -> ComposeResult:
        # header
        yield Header(name='Scrabble')

        # available letters
        tiles = [Tile(game_tile) for game_tile in self.player.tiles]

        yield Horizontal(
            self._get_board(),
            TilesGroup(tiles),
        )

    def on_mount(self) -> None:
        self.title = 'Scrabble'


class Scrabble(App[None]):
    def on_mount(self) -> None:
        players = [
            Player('Filip'),
            Player('Zuzia'),
        ]

        game = CoreGame(players, Language.POLISH)
        self.push_screen(Game(game, players[0].id))


if __name__ == '__main__':
    Scrabble().run()
