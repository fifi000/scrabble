class Tile:
    def __init__(self, symbol: str, points: int, id: str) -> None:
        self._symbol = symbol
        self._points = points
        self.id = id

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def points(self) -> int:
        return self._points

    @property
    def is_blank(self):
        return self.points == 0

    def set_blank_symbol(self, symbol: str) -> None:
        if not self.is_blank:
            raise ValueError('Cannot set blank symbol for a non-blank tile.')

        self._symbol = symbol

    def __repr__(self) -> str:
        return f'Tile(symbol={self.symbol!r}, points={self.points!r})'
