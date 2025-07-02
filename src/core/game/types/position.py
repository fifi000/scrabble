from __future__ import annotations

from collections.abc import Iterator
from typing import NamedTuple, Self

from core import tools


class Position(NamedTuple):
    """Represents a position in a grid with row and column indices.

    Attributes:
        row (int): The row index of the position.
        column (int): The column index of the position.
    """

    row: int = 0
    column: int = 0

    def left(self) -> Position:
        """Returns the position to the left of the current position. Previous column."""
        return self + (-1, 0)

    def right(self) -> Position:
        """Returns the position to the right of the current position. Next column."""
        return self + (1, 0)

    def top(self) -> Position:
        """Returns the position above the current position. Previous row."""
        return self + (0, -1)

    def bottom(self) -> Position:
        """Returns the position below the current position. Next row."""
        return self + (0, 1)

    def surrounding_positions(self) -> Iterator[Position]:
        """Yields the positions surrounding the current position in all four directions (left, right, top, bottom)."""
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

    def __lt__(self, value: tuple[int, ...]) -> bool:
        return tuple.__lt__(self, value)

    def __le__(self, value: tuple[int, ...]) -> bool:
        return tuple.__le__(self, value)

    def __gt__(self, value: tuple[int, ...]) -> bool:
        return tuple.__gt__(self, value)

    def __ge__(self, value: tuple[int, ...]) -> bool:
        return tuple.__ge__(self, value)

    def __repr__(self) -> str:
        return f'Position(row={self.row}, column={self.column})'

    @classmethod
    def zero(cls) -> Self:
        return cls(row=0, column=0)

    @staticmethod
    def get_positions_between(
        source: Position, destination: Position
    ) -> Iterator[Position]:
        """Yields all positions between two given positions in a straight line (including the source and destination).
        The positions must be aligned either horizontally or vertically.

        Args:
            source (Position): The starting position.
            destination (Position): The ending position.

        Raises:
            ValueError: If the positions are not aligned horizontally or vertically.
        """

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
