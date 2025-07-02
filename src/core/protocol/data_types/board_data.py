from typing import Self

from core.data_model import DataModel
from core.game.objects.board import Board
from core.protocol.data_types.field_data import FieldData


class BoardData(DataModel):
    """Data model for the game board."""

    rows: int
    columns: int
    fields: list[FieldData]

    @classmethod
    def from_board(cls, board: Board) -> Self:
        return cls(
            fields=[FieldData.from_field(field) for field in board.get_fields()],
            rows=board.rows,
            columns=board.columns,
        )
