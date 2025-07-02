from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import override

from textual import on
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.screen import ModalScreen

from ui.storage_manager import SessionModel
from ui.widgets.room_info import RoomInfo


class RejoinRoomsScreen(ModalScreen[SessionModel | None]):
    BINDINGS = [('escape', 'dismiss', 'Dismiss')]

    sessions: reactive[list[SessionModel]] = reactive(list, recompose=True)

    DEFAULT_CSS = """
    RejoinRoomsScreen {
        #container {
            margin: 4 8;
            border: tall $accent;
        }

        RoomInfo {
            margin: 1;
        }
    }
    """

    @override
    def compose(self) -> ComposeResult:
        with VerticalScroll(id='container'):
            if not self.sessions:
                self.sessions = [SessionModel(id='', room_number=0, uri='')]

            for session in sorted(
                self.sessions,
                key=lambda x: datetime.fromisoformat(x.datetime),
                reverse=True,
            ):
                yield RoomInfo(session)

    def update_sessions(self, sessions: Iterable[SessionModel]) -> None:
        self.sessions = list(sessions)

    @on(RoomInfo.Rejoin)
    def handle_rejoin(self, event: RoomInfo.Rejoin):
        self.dismiss(event.session)
