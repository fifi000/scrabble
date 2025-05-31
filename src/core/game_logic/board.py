import string
from collections.abc import Iterable

from core.game_logic.enums.field_type import FieldType
from core.game_logic.field import Field
from core.game_logic.position import Position
from core.game_logic.tile import Tile

ROW_COUNT, COLUMN_COUNT = 15, 15

# rows
ROW_LABELS = string.ascii_lowercase[:ROW_COUNT]
assert len(ROW_LABELS) == ROW_COUNT
assert ROW_LABELS[0] == 'a'
assert ROW_LABELS[-1] == 'o'

# columns
COLUMN_LABELS = [x + 1 for x in range(COLUMN_COUNT)]
assert len(COLUMN_LABELS) == COLUMN_COUNT
assert COLUMN_LABELS[0] == 1
assert COLUMN_LABELS[-1] == 15

_board = [
    [4, 0, 0, 1, 0, 0, 0, 4, 0, 0, 0, 1, 0, 0, 4],  # a
    [0, 3, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 3, 0],  # b
    [0, 0, 3, 0, 0, 0, 1, 0, 1, 0, 0, 0, 3, 0, 0],  # c
    [1, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 1],  # d
    [0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0],  # e
    [0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0],  # f
    [0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0],  # g
    [4, 0, 0, 1, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0, 4],  # h
    [0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0],  # i
    [0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0],  # j
    [0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0],  # k
    [1, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 1],  # l
    [0, 0, 3, 0, 0, 0, 1, 0, 1, 0, 0, 0, 3, 0, 0],  # m
    [0, 3, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 3, 0],  # n
    [4, 0, 0, 1, 0, 0, 0, 4, 0, 0, 0, 1, 0, 0, 4],  # o
]


class Board:
    def __init__(self) -> None:
        self._grid = self._create_grid()

    def _create_grid(self) -> list[list[Field]]:
        grid: list[list[Field]] = []

        for i, row in enumerate(_board):
            grid.append([])
            for j, cell in enumerate(row):
                grid[-1].append(Field(Position(i, j), FieldType(cell)))

        return grid

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def columns(self) -> int:
        return len(self.grid[0])

    @property
    def grid(self) -> list[list[Field]]:
        return self._grid

    @property
    def all_fields(self) -> Iterable[Field]:
        for row in self._grid:
            for cell in row:
                yield cell

    def try_get_field(self, row: int, column: int) -> Field | None:
        try:
            return self.get_field(row, column)
        except IndexError:
            return None

    def get_field(self, row: int, column: int) -> Field:
        if not (0 <= row < len(self._grid)):
            raise IndexError('Given row is not valid.')

        if not (0 <= column < len(self._grid[row])):
            raise IndexError('Given column is not valid.')

        return self._grid[row][column]

    def place_tiles(self, tiles: list[Tile], positions: list[Position]) -> list[Field]:
        fields: list[Field] = []

        for tile, position in zip(tiles, positions, strict=True):
            field = self.get_field(*position)
            field.tile = tile
            fields.append(field)

        return fields
