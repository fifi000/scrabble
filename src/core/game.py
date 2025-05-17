from __future__ import annotations

from functools import wraps
from uuid import UUID

from core.board import Board
from core.enums.language import Language
from core.player import Player
from core.position import Position
from core.tile import Tile
from core.tile_bag import TileBag


class Game:
    def __init__(self, language: Language) -> None:
        self.language = language
        self.letter_bag = TileBag(language)
        self.players: list[Player] = []
        self.board = Board()
        self.move = 0
        self.game_started = False

    @property
    def current_player(self) -> Player:
        return self.players[self.move % len(self.players)]

    def get_player(self, id: UUID) -> Player:
        for player in self.players:
            if player.id == id:
                return player

        raise Exception(f"Could not find a player for given '{id=}'")

    def can_play(self) -> bool:
        return True

    def is_valid_word_placement(self, positions: list[Position]) -> bool:
        return all(self.board.get_field(position).is_empty for position in positions)

    def add_player(self, player: Player) -> None:
        self.players.append(player)

    def start(self) -> None:
        if self.game_started:
            raise Exception('Game have already started.')
        self.game_started = True

        for player in self.players:
            player.tiles = self.letter_bag.scrabble(7)

    def _check_player(self, player: Player) -> None:
        if player != self.current_player:
            if player not in self.players:
                raise Exception(
                    'There is no player in game corresponding to provided player.'
                )
            else:
                raise Exception('This is not this player move.')

    @staticmethod
    def player_move(func):
        @wraps(func)
        def wrapper(self: Game, player: Player, *args, **kwargs):
            self._check_player(player)
            result = func(self, player, *args, **kwargs)
            self.move += 1
            return result

        return wrapper

    @player_move
    def exchange_letters(self, player: Player, letters: list[Tile]) -> None:
        new_letters = self.letter_bag.exchange(letters)

        for letter in letters:
            player.tiles.remove(letter)

        player.tiles.extend(new_letters)

    @player_move
    def place_tiles(
        self,
        player: Player,
        tile_ids: list[UUID],
        field_positions: list[tuple[int, int]],
    ) -> list[Tile]:
        positions = [Position(x, y) for (x, y) in field_positions]

        if not self.is_valid_word_placement(positions):
            raise Exception('Given move is not valid.')

        tiles = [player.get_tile(tile_id) for tile_id in tile_ids]

        self.board.place_tiles(tiles, positions)

        for tile in tiles:
            player.tiles.remove(tile)

        new_tiles = self.letter_bag.scrabble(len(tiles))
        player.tiles.extend(new_tiles)

        return new_tiles
