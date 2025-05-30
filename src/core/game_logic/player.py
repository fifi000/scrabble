import uuid
from core.game_logic.tile import Tile


class Player:
    def __init__(self, name: str, id: str | None = None) -> None:
        self.name = name

        self.id: str = id if id is not None else str(uuid.uuid4())
        self.tiles: list[Tile] = []
        self.scores: list[int] = []

    @property
    def score(self) -> int:
        return sum(self.scores)

    def __repr__(self) -> str:
        return f'{self.name} - {self.score}'

    def get_tile(self, tile_id: str) -> Tile:
        for tile in self.tiles:
            if tile.id == tile_id:
                return tile

        raise Exception('Did not find tile for given id.')
