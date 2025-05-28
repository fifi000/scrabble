from uuid import UUID

from core.game_logic.tile import Tile


class Player:
    def __init__(self, id: UUID, name: str) -> None:
        self.id = id
        self.name = name

        self.tiles: list[Tile] = []
        self.scores: list[int] = []

    @property
    def score(self) -> int:
        return sum(self.scores)

    def __repr__(self) -> str:
        return f'{self.name} - {self.score}'

    def get_tile(self, tile_id: UUID) -> Tile:
        for tile in self.tiles:
            if tile.id == tile_id:
                return tile

        raise Exception('Did not find tile for given id.')
