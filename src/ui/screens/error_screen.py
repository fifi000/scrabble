from typing import Any

from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.screen import Screen
from textual.widgets import Button, Pretty


class ErrorScreen(Screen):
    CSS = """
        ErrorScreen {
            padding: 4 2;

            Pretty {
                height: 1fr;
                width: 100%;
                border: round white;
            }

            Button {
                height: 3;
            }
        }
    """
    BORDER_TITLE = 'Error Message'

    def __init__(
        self,
        object: Any,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.object_ = object

    def compose(self) -> ComposeResult:
        with VerticalGroup():
            yield Pretty(self.object_)
            yield Button.error('Close', id='close')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case 'close':
                self.dismiss()

            case _:
                raise Exception(f'Unsupported button id {event.button.id!r}')
