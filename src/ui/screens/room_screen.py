from __future__ import annotations

from textual.reactive import reactive
from textual.app import ComposeResult
from textual.screen import Screen
from textual.message import Message
from textual.widgets import (
    Button,
    Label,
    ListItem,
    ListView,
)


class RoomScreen(Screen):
    class StartGame(Message):
        pass

    player_names: reactive[list[str]] = reactive(list, recompose=True)

    def __init__(
        self, room_number: int, player_names: list[str], *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self.room_number = room_number
        self.player_names = player_names

    def add_player(self, player_name: str) -> None:
        self.player_names.append(player_name)
        self.mutate_reactive(RoomScreen.player_names)

    def compose(self) -> ComposeResult:
        self.border_title = f'Room {self.room_number}'

        yield Label(f'Players ({len(self.player_names)})')
        yield ListView(*[ListItem(Label(name)) for name in self.player_names])

        yield Button.success('Start Game', id='start_game')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case 'start_game':
                self.loading = True
                self.post_message(self.StartGame())

            case _:
                raise Exception(f'Unsupported button id {event.button.id!r}')
