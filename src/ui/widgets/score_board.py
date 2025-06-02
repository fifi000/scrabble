from collections.abc import Iterable
from itertools import zip_longest

from rich.style import Style
from rich.text import Text
from textual.reactive import reactive
from textual.widgets import DataTable

from ui.models import PlayerModel


class ScoreBoard(DataTable):
    BORDER_TITLE = 'Score Board'

    players: reactive[list[PlayerModel]] = reactive(list, recompose=True)
    current_player_id = reactive(str)

    def update_players(self, players: list[PlayerModel]) -> None:
        self.players = players
        self.mutate_reactive(ScoreBoard.players)

    def update_current_player(self, player_id: str) -> None:
        self.current_player_id = player_id

    def _get_rows(self) -> Iterable:
        scores = [player.scores for player in self.players]
        rows = zip_longest(*scores, fillvalue='')

        return rows

    def on_mount(self) -> None:
        self.clear()

        for player in self.players:
            self.add_column(
                Text(
                    text=player.name,
                    style=Style(underline=player.id == self.current_player_id),
                )
            )

        for i, row in enumerate(self._get_rows(), start=1):
            self.add_row(*row, label=str(i))
