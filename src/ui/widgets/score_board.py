from collections.abc import Iterator
from itertools import zip_longest
from typing import override

from rich.style import Style
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.reactive import reactive
from textual.widgets import DataTable

from ui.models import PlayerModel


class ScoreBoard(VerticalGroup):
    BORDER_TITLE = 'Score Board'

    players: reactive[list[PlayerModel]] = reactive(list, recompose=True)
    current_player_id = reactive(str, recompose=True)

    def update_players(self, players: list[PlayerModel]) -> None:
        self.players = players

    def update_current_player(self, player_id: str) -> None:
        self.current_player_id = player_id

    def _get_rows(self) -> Iterator:
        scores = [player.scores for player in self.players]

        if not any(player_scores for player_scores in scores):
            scores = [[''] for _ in scores]

        rows = zip_longest(*scores, fillvalue='')

        return rows

    def _prepare_table(self) -> DataTable:
        table = DataTable()

        for player in self.players:
            table.add_column(
                Text(
                    text=player.name,
                    style=Style(underline=player.id == self.current_player_id),
                )
            )

        for i, row in enumerate(self._get_rows(), start=1):
            table.add_row(*row, label=str(i))

        return table

    @override
    def compose(self) -> ComposeResult:
        yield self._prepare_table()
