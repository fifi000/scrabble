from typing import Self

from core.data_model import DataModel
from core.game.objects.player import Player
from core.protocol.data_types.tile_data import TileData


class PlayerData(DataModel):
    """Data model for player information in the game."""

    id: str
    name: str
    tiles: list[TileData] | None = None
    scores: list[int] | None = None

    @classmethod
    def from_player(cls, player: Player, with_tiles: bool = False) -> Self:
        obj = cls(
            id=player.id,
            name=player.name,
            scores=player.scores,
        )

        if with_tiles:
            obj.tiles = [TileData.from_tile(tile) for tile in player.tiles]

        return obj
