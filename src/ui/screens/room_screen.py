from __future__ import annotations

from dataclasses import dataclass

from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Rule, Header, DataTable


class RoomScreen(Screen):
    def __init__(
        self, room_number: int, player_names: list[str], *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self.room_number = room_number
        self.player_names = player_names

    def compose(self) -> ComposeResult:
        yield Header(name=f'Room {self.room_number}')

        table = DataTable()
        table.add_column('Player name')
        table.add_rows(self.player_names)

        yield table

        yield Button.success('Start Game')

    # def on_button_pressed(self, event: Button.Pressed) -> None:
    #     form_info = FormInfo(
    #         server_url=self.query_one('#server_url', Input).value,
    #         player_name=self.query_one('#player_name', Input).value,
    #     )

    #     match event.button.id:
    #         case 'join':
    #             form_info.room_id = self.query_one('#room_id', Input).value
    #             self.post_message(self.JoinRoom(form_info))

    #         case 'create':
    #             self.post_message(self.CreateRoom(form_info))

    #         case _:
    #             raise Exception(f'Unsupported button id {event.button.id!r}')
