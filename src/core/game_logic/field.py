from core.game_logic.enums.field_type import FieldType
from core.game_logic.position import Position
from core.game_logic.tile import Tile


class Field:
    def __init__(
        self, position: Position, type: FieldType, tile: Tile | None = None
    ) -> None:
        self.position: Position = position
        self.type: FieldType = type
        self.tile: Tile | None = tile

    @property
    def is_empty(self) -> bool:
        return self.tile is None

    @property
    def row(self) -> int:
        return self.position.row

    @property
    def column(self) -> int:
        return self.position.column
