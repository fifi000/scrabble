from dataclasses import dataclass
from typing import override

from textual import events
from textual.app import ComposeResult
from textual.containers import Grid
from textual.css.scalar import Unit
from textual.geometry import Size
from textual.message import Message
from textual.reactive import reactive

from ui.models import BoardModel
from ui.widgets.field import Field


class Board(Grid):
    @dataclass
    class FieldSelected(Message):
        field: Field

    fields: reactive[list[Field]] = reactive(list, layout=True, recompose=True)
    board_model: reactive[BoardModel | None] = reactive(
        default=None, layout=True, recompose=True
    )

    @property
    def rows(self) -> int:
        if self.board_model is None:
            return 0
        return self.board_model.rows

    @property
    def columns(self) -> int:
        if self.board_model is None:
            return 0
        return self.board_model.columns

    @override
    def compose(self) -> ComposeResult:
        self.styles.grid_size_rows = self.rows
        self.styles.grid_size_columns = self.columns

        for field in self.fields:
            yield field

    def update(self, board_model: BoardModel) -> None:
        self.board_model = board_model
        self.fields = [Field(field) for field in self.board_model.fields]

    @override
    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        if not self.fields:
            return 0
        field = self.fields[0]

        assert field.styles.height is not None, 'Field does not have height'
        assert field.styles.height.unit == Unit.CELLS, (
            f'Field does not have height in {Unit.CELLS!r}'
        )

        row_height = int(field.styles.height.value)
        lines = self.rows + 1

        return (self.rows * row_height) + lines

    @override
    def get_content_width(self, container: Size, viewport: Size) -> int:
        if not self.fields:
            return 0
        field = self.fields[0]

        assert field.styles.width is not None, 'Field does not have width'
        assert field.styles.width.unit == Unit.CELLS, 'Field does not width in cells'

        column_width = int(field.styles.width.value)
        lines = self.columns + 1

        return (self.columns * column_width) + lines

    def on_click(self, event: events.Click) -> None:
        if isinstance(event.control, Field) and not event.control.is_locked:
            self.post_message(self.FieldSelected(event.control))
