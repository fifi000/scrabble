from __future__ import annotations

from typing import assert_never, override

from textual.reactive import reactive
from textual.widgets import Static

from core.game.enums import FieldType
from core.game.types.position import Position
from ui.models.field_model import FieldModel
from ui.widgets.tile import Tile


class Field(Static):
    tile: reactive[Tile | None] = reactive(None)

    def __init__(
        self, field_model: FieldModel, is_locked: bool = False, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self._is_locked = is_locked

        self.field_model = field_model
        if self.field_model.tile is not None:
            self._is_locked = True
            self.tile = Tile(self.field_model.tile)

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
    def position(self) -> Position:
        return Position(self.row, self.column)

    @override
    def render(self) -> str:
        if not self.tile:
            return ''
        return self.tile.text.center(self.size.width)

    def watch_tile(self, new_tile: Tile | None) -> None:
        self._update_field_style()

    def _update_field_style(self) -> None:
        self.remove_class(
            'standard',
            'double-letter',
            'triple-letter',
            'double-word',
            'triple-word',
            'tile-unlocked',
            'tile-locked',
        )

        if self.tile and self.is_locked:
            self.add_class('tile-locked')
        elif self.tile:
            self.add_class('tile-unlocked')
        else:
            # Add field type classes
            match self.type:
                case FieldType.STANDARD:
                    self.add_class('standard')
                case FieldType.DOUBLE_LETTER:
                    self.add_class('double-letter')
                case FieldType.TRIPLE_LETTER:
                    self.add_class('triple-letter')
                case FieldType.DOUBLE_WORD:
                    self.add_class('double-word')
                case FieldType.TRIPLE_WORD:
                    self.add_class('triple-word')
                case _:
                    assert_never(self.type)
