from __future__ import annotations

from textual.reactive import reactive
from textual.widgets import Static

from core.game_logic.enums.field_type import FieldType
from ui.models import FieldModel
from ui.widgets.tile import Tile


class Field(Static):
    tile: reactive[Tile | None] = reactive(None)

    def __init__(
        self, field_model: FieldModel, locked: bool = False, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self._is_locked = locked

        self.field_model = field_model
        if self.field_model.tile:
            self.tile = Tile(self.field_model.tile)
            self._is_locked = True

    @property
    def is_locked(self) -> bool:
        return self._is_locked

    @property
    def row(self) -> int:
        return self.field_model.row

    @property
    def column(self) -> int:
        return self.field_model.column

    @property
    def type(self) -> FieldType:
        return self.field_model.type

    @property
    def position(self) -> tuple[int, int]:
        return self.row, self.column

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
