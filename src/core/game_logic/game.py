from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar
from uuid import UUID

from core import tools
from core.game_logic.board import Board
from core.game_logic.enums.field_type import FieldType
from core.game_logic.enums.language import Language
from core.game_logic.field import Field
from core.game_logic.player import Player
from core.game_logic.position import Position
from core.game_logic.tile import Tile
from core.game_logic.tile_bag import TileBag

TILES_PER_ROUND = 7


T = TypeVar('T')
P = ParamSpec('P')


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
        return all(self.board.get_field(*position).is_empty for position in positions)

    def add_player(self, player: Player) -> None:
        self.players.append(player)

    def start(self) -> None:
        if self.game_started:
            raise Exception('Game have already started.')
        self.game_started = True

        for player in self.players:
            player.tiles = self.letter_bag.scrabble(TILES_PER_ROUND)

    def _check_player(self, player: Player) -> None:
        if player != self.current_player:
            if player not in self.players:
                raise Exception(
                    'There is no player in game corresponding to provided player.'
                )
            else:
                raise Exception('This is not this player move.')

    def next_turn(self) -> None:
        self.move += 1
        for field in self.board.all_fields:
            field.just_placed_tile = False

    @staticmethod
    def player_move(func: Callable[P, T]) -> Callable[P, T]:
        """
        A decorator for player move functions that ensures pre- and post-move game logic is executed.
        Args:
            func (Callable[[Game, Player, ...], T]): The function to decorate. It must take at least two parameters:
        Returns:
            Callable: The wrapped function with pre- and post-move hooks.
        """

        @wraps(func)
        def wrapper(game: Game, player: Player, *args: P.args, **kwargs: P.kwargs) -> T:
            game._check_player(player)
            result = func(game, player, *args, **kwargs)  # type: ignore
            game.next_turn()
            return result

        return wrapper  # type: ignore

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
        tile_ids: list[str],
        field_positions: list[Position],
    ) -> None:
        if not self.is_valid_word_placement(field_positions):
            raise Exception('Given move is not valid.')

        tiles = [player.get_tile(tile_id) for tile_id in tile_ids]

        fields = self.board.place_tiles(tiles, field_positions)
        for field in fields:
            field.just_placed_tile = True

        player.scores.append(self.calculate_score(fields))

        for tile in tiles:
            player.tiles.remove(tile)

        new_tiles = self.letter_bag.scrabble(len(tiles))
        player.tiles.extend(new_tiles)

    def calculate_score(self, fields: list[Field]) -> int:
        words = self.get_created_words([field.position for field in fields])

        score = 0

        # all letters placed
        if len(fields) == TILES_PER_ROUND:
            score += 50

        for word in words:
            score += Game.calculate_word_score(word)

        return score

    @staticmethod
    def calculate_word_score(fields: list[Field]) -> int:
        if len(fields) < 2:
            return 0

        old_fields, new_fields = tools.split(
            fields,
            key=lambda x: not x.just_placed_tile,
        )

        score = 0

        # old tiles - without bonus
        for field in old_fields:
            assert field.tile

            score += field.tile.points

        # new tiles - with letter bonus
        for field in new_fields:
            assert field.tile

            score += field.tile.points * Game.get_letter_bonus(field.type)

        # word bonus is accumulative
        word_bonus = 1
        for field in new_fields:
            word_bonus *= Game.get_word_bonus(field.type)

        score *= word_bonus

        return score

    @staticmethod
    def get_letter_bonus(field_type: FieldType) -> int:
        match field_type:
            case FieldType.DOUBLE_LETTER:
                return 2
            case FieldType.TRIPPLE_LETTER:
                return 3
            case _:
                return 1

    @staticmethod
    def get_word_bonus(field_type: FieldType) -> int:
        match field_type:
            case FieldType.DOUBLE_WORD:
                return 2
            case FieldType.TRIPPLE_WORD:
                return 3
            case _:
                return 1

    def get_created_words(self, positions: list[Position]) -> list[list[Field]]:
        words: list[list[Field]] = []

        # all horizonally created words
        for position in tools.distinct_by(positions, key=lambda x: x.row):
            word: list[Field] = []

            # left letters
            column = position.column - 1
            while (
                field := self.board.try_get_field(position.row, column)
            ) and field.tile:
                word.append(field)
                column -= 1

            # right letters
            column = position.column + 1
            while (
                field := self.board.try_get_field(position.row, column)
            ) and field.tile:
                word.append(field)
                column += 1

            # placed letter
            word.append(self.board.get_field(*position))

            word.sort(key=lambda x: x.column)

            words.append(word)

        # all vertically created words
        for position in tools.distinct_by(positions, key=lambda x: x.column):
            word: list[Field] = []

            # top letters
            row = position.row - 1
            while (
                field := self.board.try_get_field(row, position.column)
            ) and field.tile:
                word.append(field)
                row -= 1

            # bottom letters
            row = position.row + 1
            while (
                field := self.board.try_get_field(row, position.column)
            ) and field.tile:
                word.append(field)
                row += 1

            # placed letter
            word.append(self.board.get_field(*position))

            word.sort(key=lambda x: x.row)

            words.append(word)

        return words
