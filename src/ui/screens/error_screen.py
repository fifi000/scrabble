from typing import Any, override

from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Button, Pretty


class ErrorScreen(ModalScreen):
    CSS = """
    ErrorScreen {
        #container {
            border: heavy $accent;
            margin: 4 8;
            scrollbar-gutter: stable;
            
            Pretty {
                width: auto;
            }

            Button {
                dock: bottom;
            }
        }
    }
    """

    BINDINGS = [('escape', 'dismiss', 'Dismiss error')]

    def __init__(
        self,
        object: Any,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.object = object

    @override
    def compose(self) -> ComposeResult:
        with ScrollableContainer(id='container'):
            yield Pretty(self.object)
            yield Button.error('close', id='close')

    def on_mount(self) -> None:
        widget = self.query_one('#container')
        widget.border_title = 'Error Message'
        widget.border_subtitle = 'Escape to close'

    @on(Button.Pressed, '#close')
    def close(self) -> None:
        self.dismiss()
