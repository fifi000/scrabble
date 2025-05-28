from typing import NamedTuple


class Position(NamedTuple):
    row: int = 0
    column: int = 0

    def __repr__(self) -> str:
        return f'({self.row}, {self.column})'
