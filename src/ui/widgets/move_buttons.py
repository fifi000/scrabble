from typing import override
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button


class MoveButtons(Horizontal):
    BORDER_TITLE = 'Game Moves'

    @override
    def compose(self) -> ComposeResult:
        yield Button.success('Submit', id='submit')
        yield Button.warning('Exchange', id='exchange')
        yield Button.error('Skip', id='skip')
