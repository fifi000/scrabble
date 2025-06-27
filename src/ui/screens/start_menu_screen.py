from __future__ import annotations

import random
from dataclasses import dataclass
from typing import override

from textual.app import ComposeResult
from textual.containers import Grid, HorizontalGroup
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Input, Label


@dataclass
class FormInfo:
    server_url: str
    player_name: str
    room_number: int


class StartMenuScreen(Screen):
    @dataclass
    class JoinRoom(Message):
        form_info: FormInfo

    @dataclass
    class CreateRoom(Message):
        form_info: FormInfo

    @dataclass
    class Rejoin(Message):
        form_info: FormInfo

    @override
    def compose(self) -> ComposeResult:
        with Grid(classes='inputs'):
            yield Label('Server URL')
            yield Input(
                placeholder='ws://localhost:8765',
                value='ws://localhost:8765',
                id='server_url',
            )

            yield Label('Player name')
            yield Input(id='player_name', value='feefee')

            yield Label('Room number')
            yield Input(
                id='room_number', value=str(random.randint(1, 100_000)), type='integer'
            )

            with HorizontalGroup(id='buttons'):
                yield Button.success('Join', id='join')
                yield Button.warning('Create', id='create')
                yield Button('Rejoin', id='rejoin', variant='primary')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        form_info = FormInfo(
            server_url=self.query_one('#server_url', Input).value,
            player_name=self.query_one('#player_name', Input).value,
            room_number=int(self.query_one('#room_number', Input).value),
        )

        match event.button.id:
            case 'join':
                self.loading = True
                self.post_message(StartMenuScreen.JoinRoom(form_info))

            case 'create':
                self.loading = True
                self.post_message(StartMenuScreen.CreateRoom(form_info))

            case 'rejoin':
                self.loading = True
                self.post_message(StartMenuScreen.Rejoin(form_info))

            case _:
                raise Exception(f'Unsupported button id {event.button.id!r}')
