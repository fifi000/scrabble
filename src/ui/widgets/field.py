from __future__ import annotations
from core.enums.field_type import FieldType

from textual.widgets import Static
from textual.reactive import reactive

from ui.widgets.tile import Tile


class Field(Static):
    tile: reactive[Tile | None] = reactive(None)

    def __init__(self, type: FieldType, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.type = type

    def render(self) -> str:
        if not self.tile:
            return ''
        return self.tile.text.center(self.size.width)

    def watch_tile(self, new_tile: Tile) -> None:
        self.styles.background = Field.get_background_color(self)

    @staticmethod
    def get_background_color(field: Field) -> str | None:
        if field.tile:
            return 'yellow'

        match field.type:
            case FieldType.STANDARD:
                return None
            case FieldType.DOUBLE_LETTER:
                return '#57a9c2'
            case FieldType.TRIPPLE_LETTER:
                return '#5774c2'
            case FieldType.DOUBLE_WORD:
                return '#9c733e'
            case FieldType.TRIPPLE_WORD:
                return '#ce1717'
