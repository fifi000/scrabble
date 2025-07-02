from typing import Self

from core.data_model import DataModel
from core.game.objects.field import Field
from core.protocol.data_types.tile_data import TileData


class FieldData(DataModel):
    """Data model for field information on the game board."""

    row: int
    column: int
    type: int
    tile: TileData | None = None

    @classmethod
    def from_field(cls, field: Field) -> Self:
        obj = cls(
            row=field.row,
            column=field.column,
            type=field.type.value,
        )

        if field.tile:
            obj.tile = TileData.from_tile(field.tile)

        return obj
