from typing import Self
from core.data_model import DataModel
from core.protocol.data_types.board_data import BoardData
from ui.models.field_model import FieldModel


class BoardModel(DataModel):
    rows: int
    columns: int
    fields: list[FieldModel]

    @classmethod
    def form_board_data(cls, board_data: BoardData) -> Self:
        return cls(
            rows=board_data.rows,
            columns=board_data.columns,
            fields=[FieldModel.from_field_data(field) for field in board_data.fields],
        )

    def to_board_data(self) -> BoardData:
        return BoardData(
            rows=self.rows,
            columns=self.columns,
            fields=[field.to_field_data() for field in self.fields],
        )
