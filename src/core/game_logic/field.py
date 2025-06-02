from core.game_logic.enums.field_type import FieldType
from core.game_logic.position import Position
from core.game_logic.tile import Tile


class Field:
    def __init__(
        self, position: Position, type: FieldType, tile: Tile | None = None
    ) -> None:
        self.position = position
        self.type = type
        self.tile = tile

        self.just_placed_tile = False

    @property
    def is_empty(self) -> bool:
        return self.tile is None

    @property
    def row(self) -> int:
        return self.position.row

    @property
    def column(self) -> int:
        return self.position.column

    def __repr__(self) -> str:
        return f'Field(position={self.position}, type={self.type}, tile={self.tile})'
