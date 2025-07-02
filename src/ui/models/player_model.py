from typing import Self

from core.data_model import DataModel
from core.protocol.data_types.player_data import PlayerData
from ui.models.tile_model import TileModel


class PlayerModel(DataModel):
    id: str
    name: str
    tiles: list[TileModel]
    scores: list[int]

    @classmethod
    def empty(cls) -> Self:
        return cls(id='', name='', tiles=[], scores=[])

    @classmethod
    def from_player_data(cls, player_data: PlayerData) -> Self:
        return cls(
            id=player_data.id,
            name=player_data.name,
            tiles=[TileModel.from_tile_data(tile) for tile in player_data.tiles or []],
            scores=player_data.scores or [],
        )

    def to_player_data(self) -> PlayerData:
        player_data = PlayerData(
            id=self.id,
            name=self.name,
        )

        if self.tiles is not None:
            player_data.tiles = [tile.to_tile_data() for tile in self.tiles]

        return player_data
