from collections.abc import Iterable
import random
from typing import Generator
from core.enums.language import Language
from core.tile import Tile


class TileBag:
    def __init__(self, language: Language) -> None:
        self.language: Language = language
        self._all_tiles: list[Tile] = self._get_tiles()
        self._available_tiles: list[Tile] = self._all_tiles[:]

    def _get_tiles(self) -> list[Tile]:
        match self.language:
            case Language.POLISH:
                return list(TileBag.polish_tiles())
            case _:
                raise Exception('TODO')

    def scrabble(self, n: int) -> list[Tile]:
        if len(self._available_tiles) < n:
            raise Exception('There is not enough tiles in the bag')

        tiles = random.sample(self._available_tiles, n)

        for tile in tiles:
            self._available_tiles.remove(tile)

        return tiles

    def exchange(self, tiles: list[Tile]) -> list[Tile]:
        new_tiles = self.scrabble(len(tiles))

        self._available_tiles.extend(tiles)

        return new_tiles

    @staticmethod
    def polish_tiles() -> Iterable[Tile]:
        foo = {
            0: [('?', 2)],
            1: [
                ('A', 9),
                ('E', 7),
                ('I', 8),
                ('N', 5),
                ('O', 6),
                ('R', 4),
                ('S', 4),
                ('W', 4),
                ('Z', 5),
            ],
            2: [
                ('C', 3),
                ('D', 3),
                ('K', 3),
                ('L', 3),
                ('M', 3),
                ('P', 3),
                ('T', 3),
                ('Y', 4),
            ],
            3: [('B', 2), ('G', 2), ('H', 2), ('J', 2), ('Ł', 2), ('U', 2)],
            5: [('Ą', 1), ('Ę', 1), ('F', 1), ('Ó', 1), ('Ś', 1), ('Ż', 1)],
            6: [('Ć', 1)],
            7: [('Ń', 1)],
            9: [('Ź', 1)],
        }

        for points, collection in foo.items():
            for symbol, count in collection:
                for _ in range(count):
                    yield Tile(symbol, points)
