from __future__ import annotations

from collections.abc import Iterable
from typing import override

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static

from ui.storage_manager import SessionModel


class RejoinRoomsScreen(ModalScreen):
    BINDINGS = [('escape', 'dismiss', 'Dismiss')]

    sessions: reactive[list[SessionModel]] = reactive(list, layout=True, recompose=True)

    @override
    def compose(self) -> ComposeResult:
        room_infos: list[RoomInfo] = []
        for session in self.sessions:
            info = RoomInfo()
            info.room_number = session.room_number
            info.player_name = session.

    def on_mount(self) -> None:
        widget = self.query_one('#container')
        widget.border_title = 'Error Message'
        widget.border_subtitle = 'Escape to close'

    def update_sessions(self, sessions: Iterable[SessionModel]) -> None:
        self.sessions = list(sessions)

    def add_session(self, session: SessionModel) -> None:
        self.sessions.append(session)
        self.mutate_reactive(RejoinRoomsScreen.sessions)


class RoomsInfo(VerticalScroll):
    room_infos: reactive[list[RoomInfo]] = reactive(list, layout=True, recompose=True)

    @override
    def compose(self) -> ComposeResult:
        for room_info in self.room_infos:
            yield room_info

    def update_room_infos(self, room_infos: Iterable[RoomInfo]) -> None:
        self.room_infos = list(room_infos)

    def add_room_info(self, room_info: RoomInfo) -> None:
        self.room_infos.append(room_info)
        self.mutate_reactive(RoomsInfo.room_infos)


class RoomInfo(Static):
    room_number: reactive[int | None] = reactive(None)

    @override
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(f'Room number: {self.room_number}')
            yield Button('Rejoin', variant='primary', id='rejoin')
