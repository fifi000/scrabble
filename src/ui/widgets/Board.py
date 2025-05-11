from textual.app import ComposeResult
from textual.containers import Grid
from textual.geometry import Size
from textual.css.scalar import Unit
from textual import events

from ui.widgets.field import Field
from ui.widgets.tile import Tile
from ui.widgets.tiles_group import TilesGroup


class Board(Grid):
    def __init__(
        self, row_count: int, column_count: int, fields: list[Field], *args, **kwargs
    ) -> None:
        assert fields, 'Empty fields'
        assert row_count * column_count == len(fields)

        super().__init__(*args, **kwargs)
        self.row_count = row_count
        self.column_count = column_count

        self.fields = fields

    def on_mount(self) -> None:
        self.styles.grid_size_rows = self.row_count
        self.styles.grid_size_columns = self.column_count

    def compose(self) -> ComposeResult:
        for field in self.fields:
            yield field

    def get_content_height(self, container: Size, viewport: Size, height: int) -> int:
        field = self.fields[0]

        assert field.styles.height is not None, 'Field does not have height'
        assert field.styles.height.unit == Unit.CELLS, 'Field does not height in cells'

        row_height = int(field.styles.height.value)
        lines = self.row_count + 1

        return (self.row_count * row_height) + lines

    def get_content_width(self, container: Size, viewport: Size) -> int:
        field = self.fields[0]

        assert field.styles.width is not None, 'Field does not have width'
        assert field.styles.width.unit == Unit.CELLS, 'Field does not width in cells'

        column_width = int(field.styles.width.value)
        lines = self.column_count + 1

        return (self.column_count * column_width) + lines

    def on_click(self, event: events.Click) -> None:
        if isinstance(event.control, Field):
            group = self.app.query_one(TilesGroup)
            tile = group.query_exactly_one('.highlighted')
            if isinstance(tile, Tile):
                event.control.text = tile.text

                tile.visible = False
