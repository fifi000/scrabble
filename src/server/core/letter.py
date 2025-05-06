from __future__ import annotations
import uuid


class Letter:
    def __init__(self, symbol: str, points: int) -> None:
        self.id: uuid.UUID = uuid.uuid4()
        self.symbol: str = symbol
        self.points: int = points

    @property
    def is_blank(self):
        return self.symbol == "" and self.points == 0

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Letter):
            return False

        return self.id == value.id

    def __repr__(self) -> str:
        return f"({self.symbol}, {self.points})"
