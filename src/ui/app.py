from collections.abc import Generator
from textual.app import App, ComposeResult
from textual.widgets import Header, Static
from textual.containers import Grid


class Board(Grid):
    def compose(self) -> ComposeResult:
        rows, cols = 15, 15
        colors = Board.colors()

        for i in range(rows):
            for j in range(cols):
                widget = Static(str(i * j), classes='cell')
                widget.styles.color = next(colors)
                widget.styles.background = next(colors)
                yield widget

    @staticmethod
    def colors() -> Generator[str, None, None]:
        while True:
            yield 'white'
            yield 'black'
            yield 'black'
            yield 'white'


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
