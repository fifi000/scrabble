import random
import uuid
from collections.abc import Iterator

from core.game.enums import Language
from core.game.objects.tile import Tile


def get_tiles_for_language(language: Language) -> list[Tile]:
    match language:
        case Language.POLISH:
            return list(polish_tiles())
        case _:
            raise Exception('Unsupported language for tile bag')


def polish_tiles() -> Iterator[Tile]:
    # fmt: off
    tile_value_map = {
        0: [('?', 2)],
        1: [('A', 9), ('E', 7), ('I', 8), ('N', 5), ('O', 6), ('R', 4), ('S', 4), ('W', 4), ('Z', 5)],
        2: [('C', 3), ('D', 3), ('K', 3), ('L', 3), ('M', 3), ('P', 3), ('T', 3), ('Y', 4)],
        3: [('B', 2), ('G', 2), ('H', 2), ('J', 2), ('Ł', 2), ('U', 2)],
        5: [('Ą', 1), ('Ę', 1), ('F', 1), ('Ó', 1), ('Ś', 1), ('Ż', 1)],
        6: [('Ć', 1)],
        7: [('Ń', 1)],
        9: [('Ź', 1)],
    }
    # fmt: on

    for points, collection in tile_value_map.items():
        for symbol, count in collection:
            for _ in range(count):
                yield Tile(symbol, points, str(uuid.uuid4()))


class TileBag:
    def __init__(self, language: Language) -> None:
        self.language = language

        self._all_tiles = get_tiles_for_language(language)
        self._remaining_tiles = self._all_tiles.copy()

    @property
    def is_empty(self) -> bool:
        return self.remaining_tiles_count == 0

    @property
    def remaining_tiles_count(self) -> int:
        return len(self._remaining_tiles)

    def scrabble(self, n: int) -> list[Tile]:
        n = min(n, len(self._remaining_tiles))

        tiles = random.sample(self._remaining_tiles, n)

        for tile in tiles:
            self._remaining_tiles.remove(tile)

        return tiles

    def exchange(self, tiles: list[Tile]) -> list[Tile]:
        new_tiles = self.scrabble(len(tiles))

        self._remaining_tiles.extend(tiles)

        return new_tiles
