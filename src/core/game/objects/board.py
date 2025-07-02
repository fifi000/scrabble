from collections.abc import Iterable, Iterator
from typing import Literal, overload

from core.game.enums import FieldType
from core.game.objects.field import Field
from core.game.objects.tile import Tile
from core.game.types.position import Position
from core.game.types.square_grid import SquareGrid


class Board:
    def __init__(self, board_layout: Iterable[Iterable[FieldType]]) -> None:
        fields = [
            Field(position=Position(i, j), type=cell)
            for i, row in enumerate(board_layout)
            for j, cell in enumerate(row)
        ]

        self._grid = SquareGrid.from_flat(fields)

    @property
    def rows(self) -> int:
        return self._grid.rows

    @property
    def columns(self) -> int:
        return self._grid.columns

    @property
    def size(self) -> tuple[int, int]:
        return self._grid.size

    def get_fields(self) -> Iterator[Field]:
        yield from self._grid

    @property
    def center_field(self) -> Field:
        if self.rows < 1 or self.columns < 1:
            raise IndexError('Board does not have a center field. Board is empty.')

        if self.rows % 2 == 0 or self.columns % 2 == 0:
            raise IndexError(
                'Board does not have a center field. Board has even dimensions.'
            )

        center_row = self.rows // 2
        center_column = self.columns // 2

        try:
            return self.get_field(center_row, center_column)
        except IndexError as e:
            raise IndexError('Board does not have a center field.') from e

    def get_horizontal_fields(self, start: Position) -> Iterator[Field]:
        return self._get_fields_by_orientation(start, 'horizontal')

    def get_vertical_fields(self, start: Position) -> Iterator[Field]:
        return self._get_fields_by_orientation(start, 'vertical')

    def _get_fields_by_orientation(
        self, start: Position, orientation: Literal['horizontal', 'vertical']
    ) -> Iterator[Field]:
        if orientation == 'horizontal':
            directions = [(0, 1), (0, -1)]
        elif orientation == 'vertical':
            directions = [(1, 0), (-1, 0)]
        else:
            raise ValueError(
                f'Invalid orientation: {orientation!r}. Expected "horizontal" or "vertical".'
            )

        seen: set[Position] = set()

        for direction in directions:
            for field in self._get_fields_in_direction(start, direction):
                if field.position in seen:
                    continue

                yield field
                seen.add(field.position)

    def _get_fields_in_direction(
        self, start: Position, direction: tuple[int, int]
    ) -> Iterator[Field]:
        if direction == (0, 0):
            return start

        position = start

        while True:
            try:
                field = self.get_field(position)
            except IndexError:
                break

            if field.tile is None:
                break

            yield field
            position += direction

    @overload
    def get_field(self, position: Position, /) -> Field: ...

    @overload
    def get_field(self, row: int, column: int, /) -> Field: ...

    def get_field(
        self, position_or_row: int | Position, column: int | None = None, /
    ) -> Field:
        match (position_or_row, column):
            case (Position(), None):
                position = position_or_row
                return self._grid[position]
            case (int(), int()):
                row, column = position_or_row, column
                return self._grid[row, column]
            case _:
                raise TypeError(
                    f'Invalid arguments: {position_or_row}, {column}. '
                    'Expected Position or (row, column) pair.'
                )

    def place_tiles(self, tile_positions: list[tuple[Tile, Position]]) -> list[Field]:
        fields: list[Field] = []

        for tile, position in tile_positions:
            field = self.get_field(position)
            field.tile = tile
            field.is_tile_recently_placed = True
            fields.append(field)

        return fields
