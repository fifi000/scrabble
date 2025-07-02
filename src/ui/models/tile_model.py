from typing import Self

from core.data_model import DataModel
from core.game.types.position import Position
from core.protocol.data_types.tile_data import TileData


class TileModel(DataModel):
    id: str
    symbol: str
    points: int
    position: Position | None = None

    @classmethod
    def from_tile_data(cls, tile_data: TileData) -> Self:
        return cls(
            id=tile_data.id,
            symbol=tile_data.symbol,
            points=tile_data.points,
            position=tile_data.position,
        )

    def to_tile_data(self) -> TileData:
        return TileData(
            id=self.id, symbol=self.symbol, points=self.points, position=self.position
        )
