from textual.containers import Horizontal
from textual.app import ComposeResult
from textual.widgets import Button


class MoveButtons(Horizontal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.submit_button = Button.success('Submit')
        self.exchange_button = Button.warning('Exchange')
        self.skip_button = Button.error('Skip')

    def compose(self) -> ComposeResult:
        yield self.submit_button
        yield self.exchange_button
        yield self.skip_button
