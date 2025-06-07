from core.game.objects.tile import Tile


class Player:
    def __init__(self, name: str, id: str) -> None:
        self.name = name
        self.id = id

        self.tiles: list[Tile] = []
        self.scores: list[int] = []

    @property
    def score(self) -> int:
        return sum(self.scores)

    def add_score(self, score: int) -> None:
        self.scores.append(score)

    def add_tile(self, tile: Tile) -> None:
        self.tiles.append(tile)

    def add_tiles(self, tiles: list[Tile]) -> None:
        self.tiles.extend(tiles)

    def remove_tile(self, tile: Tile) -> None:
        try:
            self.tiles.remove(tile)
        except ValueError as e:
            raise ValueError("Tile not found in player's tiles.") from e

    def remove_tiles(self, tiles: list[Tile]) -> None:
        for tile in tiles:
            self.remove_tile(tile)

    def replace_tiles(self, old: list[Tile], new: list[Tile]) -> None:
        self.remove_tiles(old)
        self.add_tiles(new)

    def has_tile(self, tile: Tile) -> bool:
        return tile in self.tiles

    def get_tile_by_id(self, tile_id: str) -> Tile:
        if not (tile := self.try_get_tile_by_id(tile_id)):
            raise ValueError(f"Tile with id {tile_id!r} not found in player's tiles.")

        return tile

    def try_get_tile_by_id(self, tile_id: str) -> Tile | None:
        for tile in self.tiles:
            if tile.id == tile_id:
                return tile

        return None

    def __repr__(self) -> str:
        return f'Player(name={self.name}, id={self.id}, score={self.score})'
