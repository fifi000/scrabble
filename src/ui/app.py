import random
import string
from uuid import UUID

from textual.app import App, ComposeResult
from textual.widgets import Header, Static

from core.enums.language import Language
from core.game import Game
from core.player import Player
from ui.widgets.Board import Board
from ui.widgets.Tile import Tile


def get_piece() -> str:
    if random.random() > 0.7:
        return random.choice(string.ascii_uppercase) + random.choice(
            ['₀', '₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉']
        )
    else:
        return str()


class ScrabbleApp(App):
    CSS_PATH = 'scrabble.tcss'

    def __init__(self, game: Game, player_id: UUID, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.game = game
        self.player_id = player_id

    @property
    def player(self) -> Player:
        return self.game.get_player(self.player_id)

    def compose(self) -> ComposeResult:
        # header
        yield Header(name='Scrabble')

        # board grid
        yield Board(15, 15, [Tile(get_piece(), classes='cell') for _ in range(15 * 15)])

        # available letters
        letters = [letter.symbol for letter in self.player.letters]
        text = ' '.join(letters)
        yield Static(f'Available letters: {text}')

    def on_mount(self) -> None:
        self.title = 'Scrabble'


def main() -> None:
    players = [
        Player('Filip'),
        Player('Zuzia'),
    ]

    game = Game(players, Language.POLISH)

    app = ScrabbleApp(game, players[0].id)
    app.run()


if __name__ == '__main__':
    main()
