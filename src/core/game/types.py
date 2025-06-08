from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import Any, NamedTuple, overload

from core import tools


class Position(NamedTuple):
    row: int = 0
    column: int = 0

    def left(self) -> Position:
        return self + (-1, 0)

    def right(self) -> Position:
        return self + (1, 0)

    def top(self) -> Position:
        return self + (0, -1)

    def bottom(self) -> Position:
        return self + (0, 1)

    def surrounding_positions(self) -> Iterator[Position]:
        yield self.left()
        yield self.right()
        yield self.top()
        yield self.bottom()

    def __add__(self, other: object) -> Position:
        if isinstance(other, tuple):
            row, column = other
            return Position(row=self.row + row, column=self.column + column)
        return NotImplemented

    def __sub__(self, other: object) -> Position:
        if isinstance(other, tuple):
            row, column = other
            return Position(row=self.row - row, column=self.column - column)
        return NotImplemented

    def __repr__(self) -> str:
        return f'Position(row={self.row}, column={self.column})'

    @staticmethod
    def get_positions_between(
        source: Position, destination: Position
    ) -> Iterator[Position]:
        # horizontal line
        if source.row == destination.row:
            start, end = tools.min_max([source.column, destination.column])
            while start <= end:
                yield Position(row=source.row, column=start)
                start += 1
        # vertical line
        elif source.column == destination.column:
            start, end = tools.min_max([source.row, destination.row])
            while start <= end:
                yield Position(row=start, column=source.column)
                start += 1
        else:
            raise ValueError(
                'Positions are neither aligned horizontally nor vertically.'
            )


def _is_square(data: Sequence[Sequence[Any]]) -> bool:
    row_count = len(data)

    for row in data:
        if len(row) != row_count:
            return False

    return True


class Grid[T]:
    def __init__(self, data: Sequence[Sequence[T]], /) -> None:
        if len(data) == 0:
            raise ValueError('Grid data must have at least one row.')

        if len(data[0]) == 0:
            raise ValueError('Grid data must have at least one column.')

        if not _is_square(data):
            raise ValueError(
                'Grid data must be square (same number of rows and columns).'
            )

        self._data: tuple[tuple[T, ...], ...] = tuple(tuple(row) for row in data)
        self._rows = len(self._data)
        self._columns = len(self._data[0])

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def columns(self) -> int:
        return self._columns

    @property
    def size(self) -> tuple[int, int]:
        return self.rows, self.columns

    def get_rows(self) -> Iterator[Sequence[T]]:
        for row in self._data:
            yield row

    def get_columns(self) -> Iterator[Sequence[T]]:
        for column in zip(*self._data):
            yield column

    def transpose(self) -> Grid[T]:
        transposed_data = tuple(zip(*self._data))

        return Grid(transposed_data)

    @staticmethod
    def from_flat[Item](data: Sequence[Item]) -> Grid[Item]:
        def _is_perfect_square_number(number: int) -> bool:
            if number < 0:
                return False

            root = int(number**0.5)
            return root * root == number and root > 0

        length = len(data)
        if not _is_perfect_square_number(length):
            raise ValueError(
                'Data length must be a perfect square to form a square grid.'
            )

        side_length = int(length**0.5)

        rows = [
            [data[i * side_length + j] for j in range(side_length)]
            for i in range(side_length)
        ]

        return Grid(rows)

    def __len__(self) -> int:
        return self.rows * self.columns

    def __iter__(self) -> Iterator[T]:
        for row in self.get_rows():
            for cell in row:
                yield cell

    @overload
    def __getitem__(self, index: Position, /) -> T: ...

    @overload
    def __getitem__(self, index: tuple[int, int], /) -> T: ...

    def __getitem__(self, index: tuple[int, int] | Position, /) -> T:
        if isinstance(index, Position):
            row, column = index.row, index.column
        else:
            row, column = index

        if not (0 <= row < self.rows):
            raise IndexError(f'Row index {row} out of range.')
        if not (0 <= column < self.columns):
            raise IndexError(f'Column index {column} out of range.')

        return self._data[row][column]

    def __contains__(self, key: object, /) -> bool:
        for item in self:
            if item == key:
                return True

        return False
