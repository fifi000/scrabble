from __future__ import annotations

from dataclasses import dataclass

from textual.app import ComposeResult
from textual.containers import Grid
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Input, Label


@dataclass
class FormInfo:
    server_url: str
    player_name: str
    room_number: int


class StartMenuScreen(Screen):
    class JoinRoom(Message):
        def __init__(self, form_info: FormInfo) -> None:
            super().__init__()
            self.form_info = form_info

    class CreateRoom(Message):
        def __init__(self, form_info: FormInfo) -> None:
            super().__init__()
            self.form_info = form_info

    def compose(self) -> ComposeResult:
        with Grid():
            yield Label('Server URL')
            yield Input(
                placeholder='ws://localhost:8765',
                value='ws://localhost:8765',
                id='server_url',
            )

            yield Label('Player name')
            yield Input(id='player_name', value='feefee')

            yield Label('Room number')
            yield Input(id='room_number', value='1234', type='integer')

            yield Button.success('Join', id='join')
            yield Button.warning('Create', id='create')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        form_info = FormInfo(
            server_url=self.query_one('#server_url', Input).value,
            player_name=self.query_one('#player_name', Input).value,
            room_number=int(self.query_one('#room_number', Input).value),
        )

        match event.button.id:
            case 'join':
                self.loading = True
                self.post_message(self.JoinRoom(form_info))

            case 'create':
                self.loading = True
                self.post_message(self.CreateRoom(form_info))

            case _:
                raise Exception(f'Unsupported button id {event.button.id!r}')
