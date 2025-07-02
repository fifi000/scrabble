from typing import Self

from core.data_model import DataModel
from core.game.objects.tile import Tile
from core.game.types.position import Position


class TileData(DataModel):
    """Data model for tile information in the game."""

    id: str
    symbol: str
    points: int
    position: Position | None = None

    @classmethod
    def from_tile(cls, tile: Tile, position: Position | None = None) -> Self:
        return cls(
            id=tile.id,
            symbol=tile.symbol,
            points=tile.points,
            position=position,
        )
