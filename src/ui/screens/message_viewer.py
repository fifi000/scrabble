from typing import Any

from textual.app import ComposeResult
from textual.screen import Screen
from textual.visual import VisualType
from textual.widgets import Button, Label, Pretty


class MessageViewer(Screen):
    CSS = """
        MessageViewer{
            align: center middle;
        }
        Label {
            border: tall;
        }
        Pretty {
            border: round;
        }
    """

    def __init__(self, text: VisualType, data: Any, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.text = text
        self.data = data

    def compose(self) -> ComposeResult:
        yield Label(self.text)
        yield Pretty(self.data)

        yield Button.error('Quit', id='quit')
        yield Button('Cancel', variant='primary', id='cancel')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'quit':
            self.dismiss(True)
        else:
            self.dismiss(False)
