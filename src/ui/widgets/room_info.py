from __future__ import annotations

from dataclasses import dataclass
from typing import override

from textual import on
from textual.app import ComposeResult
from textual.containers import Grid, Horizontal
from textual.message import Message
from textual.widgets import Button, Input, Label, Static

from ui.storage_manager import SessionModel


class RoomInfo(Static):
    @dataclass
    class Rejoin(Message):
        session: SessionModel

    DEFAULT_CSS = """
    RoomInfo {
        #list {
            height: auto;
        }
    }
    """

    def __init__(self, session: SessionModel, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.session = session

    @override
    def compose(self) -> ComposeResult:
        with Horizontal(id='list'):
            with Grid(classes='inputs'):
                yield Label('Room number')
                yield Input(
                    id='room_number',
                    value=str(self.session.room_number),
                    type='integer',
                )

                yield Label('Session ID')
                yield Input(id='session_id', value=self.session.id)

                yield Label('Uri')
                yield Input(id='uri', value=self.session.uri)

                yield Button('Rejoin', variant='primary', id='rejoin')

    @on(Button.Pressed, '#rejoin')
    def handle_rejoin(self, event: Button.Pressed) -> None:
        room_number = self.query_one('room_number', Input).value
        session_id = self.query_one('session_id', Input).value
        uri = self.query_one('uri', Input).value

        session = SessionModel(
            id=session_id, room_number=int(room_number or '0'), uri=uri
        )

        self.post_message(RoomInfo.Rejoin(session))
