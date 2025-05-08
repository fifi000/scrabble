from textual.app import ComposeResult
from textual.containers import Grid
from textual.widget import Widget


class Board(Grid):
    def __init__(
        self, row_count: int, column_count: int, widgets: list[Widget], *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self.row_count = row_count
        self.column_count = column_count

        self._height = self.row_count * 2
        self._width = self._height * 2

        Board.DEFAULT_CSS = f"""
        Board {{
            grid-size: {self.row_count} {self.column_count};
            
            height: {self._height};
            width: {self._width};
            background: green;
        }}
        """

        self.widgets = widgets

    def compose(self) -> ComposeResult:
        for widget in self.widgets:
            yield widget
