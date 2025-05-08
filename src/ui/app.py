import random
import string
from textual.app import App, ComposeResult
from textual.widgets import Header, Static
from textual.containers import Grid


def get_piece() -> str:
    return random.choice(string.ascii_uppercase) + random.choice(
        ['₀', '₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉']
    )


class Board(Grid):
    def compose(self) -> ComposeResult:
        rows, cols = 15, 15

        for _ in range(rows * cols):
            yield Static(get_piece(), classes='cell')


class ScrabbleApp(App):
    CSS_PATH = 'scrabble.tcss'

    def compose(self) -> ComposeResult:
        # header
        yield Header(name='Scrabble')

        # board grid
        yield Board()

        # available letters
        yield Static('Available letters')

    def on_mount(self) -> None:
        self.title = 'Scrabble'


if __name__ == '__main__':
    app = ScrabbleApp()
    app.run()
