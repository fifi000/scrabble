from __future__ import annotations
from dataclasses import dataclass
from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, Rule, Button
from textual.message import Message


class StartMenuScreen(Screen):
    @dataclass
    class FormInfo:
        server_url: str
        player_name: str
        room_id: str | None = None

    class JoinRoom(Message):
        def __init__(self, form_info: StartMenuScreen.FormInfo) -> None:
            super().__init__()

    class CreateRoom(Message):
        def __init__(self, form_info: StartMenuScreen.FormInfo) -> None:
            super().__init__()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(placeholder='server URL', id='server_url')
            yield Input(placeholder='gimme some cool nickname', id='player_name')

            yield Rule()

            with Vertical():
                yield Input(placeholder='room id', id='room_id')
                yield Button.success("Let's join!!!", id='join')

            yield Rule()

            yield Button.warning('Create new room', id='create')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        form_info = self.FormInfo(
            server_url=self.query_one('#server_url', Input).value,
            player_name=self.query_one('#player_name', Input).value,
        )

        match event.button.id:
            case 'join':
                form_info.room_id = self.query_one('#room_id', Input).value
                self.post_message(self.JoinRoom(form_info))

            case 'create':
                self.post_message(self.CreateRoom(form_info))

            case _:
                raise Exception(f'Unsupported button id {event.button.id!r}')
