from typing import Self

from core.data_model import DataModel
from core.game.enums import FieldType
from core.protocol.data_types.field_data import FieldData
from ui.models.tile_model import TileModel


class FieldModel(DataModel):
    row: int
    column: int
    type: FieldType
    tile: TileModel | None = None

    @classmethod
    def from_field_data(cls, field_data: FieldData) -> Self:
        field_model = cls(
            row=field_data.row,
            column=field_data.column,
            type=FieldType(field_data.type),
        )

        if field_data.tile is not None:
            field_model.tile = TileModel.from_tile_data(field_data.tile)

        return field_model

    def to_field_data(self) -> FieldData:
        field_data = FieldData(
            row=self.row,
            column=self.column,
            type=self.type.value,
        )

        if self.tile:
            field_data.tile = self.tile.to_tile_data()

        return field_data
