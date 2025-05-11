from __future__ import annotations
import uuid


class Tile:
    def __init__(self, letter: str, points: int) -> None:
        self.id: uuid.UUID = uuid.uuid4()
        self.symbol: str = letter
        self.points: int = points

    @property
    def is_blank(self):
        return self.symbol == '?' and self.points == 0

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Tile):
            return False

        return self.id == value.id

    def __repr__(self) -> str:
        return f'({self.symbol}, {self.points})'
