from core.game.enums import FieldType
from core.game.objects.tile import Tile
from core.game.types.position import Position


class Field:
    def __init__(
        self, position: Position, type: FieldType, tile: Tile | None = None
    ) -> None:
        self.position = position
        self.type = type
        self.tile = tile

        self.is_tile_recently_placed: bool = False

    @property
    def row(self) -> int:
        return self.position.row

    @property
    def column(self) -> int:
        return self.position.column

    def __repr__(self) -> str:
        return f'Field(position={self.position}, type={self.type}, tile={self.tile})'
