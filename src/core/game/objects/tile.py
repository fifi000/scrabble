class Tile:
    def __init__(self, symbol: str, points: int, id: str) -> None:
        self.symbol = symbol
        self.points = points
        self.id = id

    @property
    def is_blank(self):
        return self.points == 0

    def __repr__(self) -> str:
        return f'Tile(symbol={self.symbol}, points={self.points})'
