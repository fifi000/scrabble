from __future__ import annotations

import uuid


class Tile:
    def __init__(self, symbol: str, points: int, id: str | None = None) -> None:
        self.symbol: str = symbol
        self.points: int = points
        self.id: str = id if id is not None else str(uuid.uuid4())

        self.is_placed = False

    @property
    def is_blank(self):
        return self.symbol == '?' and self.points == 0

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Tile):
            return False

        return self.id == value.id

    def __repr__(self) -> str:
        return f'Tile({self.symbol}, {self.points})'
