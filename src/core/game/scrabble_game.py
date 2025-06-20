from __future__ import annotations

import random
from collections.abc import Callable, Collection, Iterable
from dataclasses import dataclass
from functools import wraps
from typing import assert_never

from core import tools
from core.exceptions.game import (
    GameAlreadyStartedError,
    GameFinishedError,
    GameNotInProgressError,
    GameStartFailureError,
    InvalidMoveError,
    InvalidOperationError,
    PlayerAlreadyExistsError,
    PlayerNotFoundError,
)
from core.game.enums import FieldType, GameState, Language
from core.game.objects.board import Board
from core.game.objects.field import Field
from core.game.objects.player import Player
from core.game.objects.tile import Tile
from core.game.objects.tile_bag import TileBag
from core.game.types import Position


def _convert_grid(grid: list[list[int]]) -> list[list[FieldType]]:
    return [[FieldType(cell) for cell in row] for row in grid]


@dataclass
class GameConfig:
    """Configuration for the Scrabble game.

    Attributes:
        tiles_per_round (int): Number of tiles each player receives at the start of each round.
        min_players (int): Minimum number of players required to start the game.
        max_players (int): Maximum number of players allowed in the game.
        min_word_length (int): Minimum length of a word that can be formed with the tiles.
        language (Language): Language of the game, which determines the tile set.
        board_layout (list[list[FieldType]]): Layout of the game board represented as a grid of FieldType.

    Raises:
        ValueError: If any of the attributes are invalid.
    """

    tiles_per_round: int
    min_players: int
    max_players: int
    min_word_length: int
    language: Language
    board_layout: list[list[FieldType]]

    def __post_init__(self) -> None:
        if self.tiles_per_round < 1:
            raise ValueError('Tiles per round must be at least 1.')

        if self.min_players < 1:
            raise ValueError('Minimum players must be at least 1.')

        if self.max_players < 1:
            raise ValueError('Maximum players must be at least 1.')

        if self.min_players > self.max_players:
            raise ValueError('Minimum players cannot be greater than maximum players.')

        if self.min_word_length < 1:
            raise ValueError('Minimum word length must be at least 1.')

        if self.min_word_length > self.tiles_per_round:
            raise ValueError(
                'Minimum word length cannot be greater than tiles per round.'
            )

        if not self.board_layout or not any(self.board_layout):
            raise ValueError('Board cannot be empty.')

        if not all(len(row) == len(self.board_layout[0]) for row in self.board_layout):
            raise ValueError(
                'Board must be a rectangular grid (all rows must have the same length).'
            )

    @staticmethod
    def default() -> GameConfig:
        """Returns the default game configuration for Scrabble with the 15x15 board."""

        return GameConfig(
            tiles_per_round=7,
            min_players=1,
            max_players=4,
            min_word_length=2,
            language=Language.POLISH,
            board_layout=_convert_grid(
                [
                    [4, 0, 0, 1, 0, 0, 0, 4, 0, 0, 0, 1, 0, 0, 4],  # a
                    [0, 3, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 3, 0],  # b
                    [0, 0, 3, 0, 0, 0, 1, 0, 1, 0, 0, 0, 3, 0, 0],  # c
                    [1, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 1],  # d
                    [0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0],  # e
                    [0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0],  # f
                    [0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0],  # g
                    [4, 0, 0, 1, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0, 4],  # h
                    [0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0],  # i
                    [0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0],  # j
                    [0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0],  # k
                    [1, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 1],  # l
                    [0, 0, 3, 0, 0, 0, 1, 0, 1, 0, 0, 0, 3, 0, 0],  # m
                    [0, 3, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 3, 0],  # n
                    [4, 0, 0, 1, 0, 0, 0, 4, 0, 0, 0, 1, 0, 0, 4],  # o
                ]
            ),
        )


def player_move[**P, TResult](func: Callable[P, TResult]) -> Callable[P, TResult]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> TResult:
        game = tools.find_arg(args, kwargs, ScrabbleGame)
        player = tools.find_arg(args, kwargs, Player)

        score_count = len(player.scores)

        game.before_turn(player)
        result = func(*args, **kwargs)
        game.after_turn()

        assert len(player.scores) == score_count + 1, (
            "Player's score should be updated after a turn."
        )

        return result

    return wrapper


class ScrabbleGame:
    def __init__(
        self, config: GameConfig, *, players: list[Player] | None = None
    ) -> None:
        self.config = config
        self._players: list[Player] = []

        self._tile_bag = TileBag(self.config.language)

        self._board = Board(self.config.board_layout)

        self._move_count: int = 0
        self._state: GameState = GameState.GAME_NOT_STARTED

        # using `add_player` method in order to validate data
        # also has to be done after all fields are initialized
        for player in players or []:
            self.add_player(player)

    @property
    def players(self) -> Collection[Player]:
        return tuple(self._players)

    @property
    def board(self) -> Board:
        return self._board

    @property
    def language(self) -> Language:
        return self.config.language

    @property
    def state(self) -> GameState:
        return self._state

    @property
    def move_count(self) -> int:
        return self._move_count

    @property
    def round_count(self) -> int:
        if self.state == GameState.GAME_NOT_STARTED:
            return 0

        assert self._players, 'Game has no players, cannot calculate round count.'

        return (self.move_count // len(self._players)) + 1

    @property
    def current_player(self) -> Player:
        match self.state:
            case GameState.GAME_NOT_STARTED:
                raise GameNotInProgressError(
                    'There is no current player, game has not been started yet.'
                )
            case GameState.GAME_FINISHED:
                raise GameFinishedError(
                    'There is no current player, game has already finished.'
                )
            case GameState.GAME_IN_PROGRESS:
                assert self._players, (
                    'Game has no players, cannot determine current player.'
                )

                return self._players[self.move_count % len(self._players)]
            case _:
                assert_never(self.state)

    # --- player ---

    def add_player(self, player: Player) -> None:
        if self.state != GameState.GAME_NOT_STARTED:
            raise InvalidOperationError(
                'Cannot add player to game that has already been started.'
            )

        if self.find_player_by_id(player.id):
            raise PlayerAlreadyExistsError(player_id=player.id, player_name=player.name)

        self._players.append(player)

    def find_player_by_id(self, player_id: str) -> Player | None:
        for player in self._players:
            if player.id == player_id:
                return player

        return None

    # --- game ---

    def start(self) -> None:
        if self.state != GameState.GAME_NOT_STARTED:
            raise GameAlreadyStartedError()

        self._verify_min_players()
        self._verify_max_players()
        self._verify_enough_tiles()

        # asign tiles
        for player in self._players:
            player.tiles = self._tile_bag.scrabble(self.config.tiles_per_round)

        # set random player order
        random.shuffle(self._players)

        self._move_count = 0

        self._state = GameState.GAME_IN_PROGRESS

        # after game start assertions
        assert self.current_player is not None, (
            'Current player must be set after starting the game.'
        )
        assert self.round_count == 1, 'Round count should be 1 after starting the game.'

    # --- turn logic ---

    def before_turn(self, player: Player) -> None:
        self._verify_game_in_progress()
        self._verify_player_in_game(player)
        self._verify_is_player_turn(player)

    def after_turn(self) -> None:
        for field in self.board.get_fields():
            field.is_tile_recently_placed = False

        self._move_count += 1

    # --- player moves ---

    @player_move
    def place_tiles(
        self,
        player: Player,
        tile_positions: list[tuple[Tile, Position]],
        *,
        blank_symbols: list[tuple[Tile, str]] | None = None,
    ) -> None:
        tiles, positions = tools.split_pairs(tile_positions)
        blank_symbols = blank_symbols or []

        self._verify_min_tiles(tiles)
        self._verify_max_tiles(tiles)
        self._verify_tiles_placements(positions)
        self._verify_tiles_ownership(player, tiles)
        self._verify_is_valid_symbols([symbol for tile, symbol in blank_symbols])

        fields = self.board.place_tiles(tile_positions)

        for tile, symbol in blank_symbols:
            tile.set_blank_symbol(symbol)

        score = self._calculate_score(fields)
        player.add_score(score)

        new_tiles = self._tile_bag.scrabble(len(tiles))
        player.replace_tiles(old=tiles, new=new_tiles)

    @player_move
    def exchange_tiles(self, player: Player, tiles: list[Tile]) -> None:
        self._verify_min_tiles(tiles)
        self._verify_max_tiles(tiles)
        self._verify_tiles_ownership(player, tiles)

        player.add_score(0)

        new_tiles = self._tile_bag.exchange(tiles)
        player.replace_tiles(old=tiles, new=new_tiles)

    @player_move
    def skip_turn(self, player: Player) -> None:
        # 'player_move' decorator does most of the work
        player.add_score(0)

    # --- verifiers ---

    def _verify_game_in_progress(self) -> None:
        match self.state:
            case GameState.GAME_NOT_STARTED:
                raise GameNotInProgressError('Game has not been started yet.')
            case GameState.GAME_IN_PROGRESS:
                return
            case GameState.GAME_FINISHED:
                raise GameFinishedError()
            case _:
                assert_never(self.state)

    def _verify_min_tiles(self, tiles: list[Tile]) -> None:
        if len(tiles) == 0:
            raise InvalidMoveError('No tiles provided.')

    def _verify_max_tiles(self, tiles: list[Tile]) -> None:
        if len(tiles) > self.config.tiles_per_round:
            raise InvalidMoveError(
                message=f'Cannot use more than {self.config.tiles_per_round} tiles in one turn.',
                details={
                    'max_tiles': self.config.tiles_per_round,
                    'tiles': len(tiles),
                },
            )

    def _verify_tiles_placements(self, positions: list[Position]) -> None:
        self._verify_fields_availability(positions)
        self._verify_tiles_make_continuous_line(positions)
        self._verify_first_or_next_move_placement(positions)

    def _verify_fields_availability(self, positions: list[Position]) -> None:
        for position in positions:
            # field must exist on board
            try:
                field = self.board.get_field(position)
            except IndexError as e:
                raise InvalidMoveError(
                    message='Field does not exist on board.',
                    details={
                        'position': position,
                        'board_size': self.board.size,
                    },
                ) from e

            # field cannot be already occupied
            if field.tile is not None:
                raise InvalidMoveError(
                    message='Field is already occupied by another tile.',
                    details={
                        'position': position,
                        'tile_id': field.tile.id,
                    },
                )

    def _verify_tiles_make_continuous_line(self, positions: list[Position]) -> None:
        # same rows --> horizontal alignment
        if tools.all_same(position.row for position in positions):
            start, end = tools.min_max(positions, key=lambda x: x.column)
        # same columns --> vertical alignment
        elif tools.all_same(position.column for position in positions):
            start, end = tools.min_max(positions, key=lambda x: x.row)
        else:
            raise InvalidMoveError(
                message='Tiles must be placed in one line, either horizontally or vertically.',
                details={
                    'positions': positions,
                },
            )

        positions_between = list(Position.get_positions_between(start, end))
        for position in positions_between:
            # tile position that player just placed
            if position in positions:
                continue

            # if not just placed, then there should already have been a tile placed
            field = self.board.get_field(position)
            if field.tile is None:
                raise InvalidMoveError(
                    message='Tiles must be placed in a continuous line.',
                    details={
                        'empty_position': position,
                    },
                )

    def _verify_first_or_next_move_placement(self, positions: list[Position]) -> None:
        # this method could be replace with a BFS, where we find if the center field
        # is reachable from any player's position
        # but this way seems to be more readable and we get straightforward error messages

        center_position = self.board.center_field.position
        is_first_move = all(field.tile is None for field in self.board.get_fields())

        # on first tile placement, tiles must go through the center field
        if is_first_move and center_position not in positions:
            raise InvalidMoveError(
                message='First placement must go through the center field.',
                details={
                    'center_field': self.board.center_field.position,
                    'positions': positions,
                },
            )

        # on any other move, tiles must be placed next to already placed tiles
        if not is_first_move:
            surrounding_positions = (
                x
                for position in positions
                for x in position.surrounding_positions()
                if x not in positions
            )

            for surrounding_position in surrounding_positions:
                try:
                    # found adjacent tile that have been already there
                    if self.board.get_field(surrounding_position).tile is not None:
                        break
                except IndexError:
                    continue
            else:
                raise InvalidMoveError(
                    message='Tiles must be placed next to already placed tiles.',
                    details={
                        'positions': positions,
                    },
                )

    def _verify_tiles_ownership(self, player: Player, tiles: list[Tile]) -> None:
        wrong_tiles: list[Tile] = []

        for tile in tiles:
            if not player.has_tile(tile):
                wrong_tiles.append(tile)

        if wrong_tiles:
            raise InvalidOperationError(
                message='Tiles do not belong to player.',
                details={'tile_ids': [tile.id for tile in wrong_tiles]},
            )

    def _verify_min_players(self) -> None:
        if len(self._players) < self.config.min_players:
            raise GameStartFailureError(
                message=f'Cannot start game with less than {self.config.min_players} players.',
                details={
                    'min_players': self.config.min_players,
                    'players': len(self._players),
                },
            )

    def _verify_max_players(self) -> None:
        if len(self._players) > self.config.max_players:
            raise GameStartFailureError(
                message=f'Cannot start game with more than {self.config.max_players} players.',
                details={
                    'max_players': self.config.max_players,
                    'players': len(self._players),
                },
            )

    def _verify_enough_tiles(self) -> None:
        needed_tiles = len(self._players) * self.config.tiles_per_round

        if self._tile_bag.remaining_tiles_count < needed_tiles:
            raise GameStartFailureError(
                message=f'Not enough tiles in bag to start game with {len(self._players)} players.',
                details={
                    'tiles': self._tile_bag.remaining_tiles_count,
                    'needed_tiles': needed_tiles,
                    'players': len(self._players),
                    'tiles_per_round': self.config.tiles_per_round,
                },
            )

    def _verify_player_in_game(self, player: Player) -> None:
        if not self.find_player_by_id(player.id):
            raise PlayerNotFoundError(player_id=player.id)

    def _verify_is_player_turn(self, player: Player) -> None:
        if not (current_player := self.current_player):
            raise InvalidOperationError(
                'Cannot obtain current player, game has not been started yet.'
            )

        if player.id != current_player.id:
            raise InvalidMoveError(
                message='It is not your turn.',
                details={
                    'current_player_id': current_player.id,
                    'current_player_name': current_player.name,
                    'player_id': player.id,
                    'player_name': player.name,
                },
            )

    def _verify_is_valid_symbols(self, symbols: Iterable[str]) -> None:
        valid_letters = self._tile_bag.all_letters(with_blank=False)

        for symbol in symbols:
            if symbol not in valid_letters:
                raise InvalidOperationError(
                    message=f'Invalid symbol: {symbols}.',
                    details={
                        'valid_symbols': valid_letters,
                    },
                )

    # --- score ---

    def _calculate_score(self, fields: list[Field]) -> int:
        assert all(field.tile for field in fields), (
            'All fields must have a tile placed on them to calculate score.'
        )

        words = self._get_created_words([field.position for field in fields])
        words = filter(lambda x: len(x) >= self.config.min_word_length, words)

        score = 0

        # all letters placed bonus
        if len(fields) == self.config.tiles_per_round:
            score += 50

        for word in words:
            score += ScrabbleGame._calculate_word_score(word)

        return score

    def _get_created_words(self, positions: list[Position]) -> list[list[Field]]:
        horizontal_words = [
            list(self.board.get_horizontal_fields(position))
            for position in tools.distinct_by(positions, key=lambda x: x.row)
        ]

        vertical_words = [
            list(self.board.get_vertical_fields(position))
            for position in tools.distinct_by(positions, key=lambda x: x.column)
        ]

        return horizontal_words + vertical_words

    @staticmethod
    def _calculate_word_score(fields: list[Field]) -> int:
        assert fields, 'Fields should not be empty when calculating word score.'
        assert all(field.tile is not None for field in fields), (
            'All fields must have a tile placed on them.'
        )

        new_fields, old_fields = tools.split(
            fields, key=lambda x: x.is_tile_recently_placed
        )

        score = 0

        # old tiles - without bonus
        for field in old_fields:
            assert field.tile, 'All fields must have a tile placed on them.'
            score += field.tile.points

        # new tiles - with letter bonus
        for field in new_fields:
            assert field.tile, 'All fields must have a tile placed on them.'
            score += field.tile.points * ScrabbleGame.get_letter_bonus(field.type)

        # word bonus is accumulative
        word_bonus = 1
        for field in new_fields:
            word_bonus *= ScrabbleGame.get_word_bonus(field.type)

        score *= word_bonus

        return score

    @staticmethod
    def get_letter_bonus(field_type: FieldType) -> int:
        match field_type:
            case FieldType.DOUBLE_LETTER:
                return 2
            case FieldType.TRIPLE_LETTER:
                return 3
            case _:
                return 1

    @staticmethod
    def get_word_bonus(field_type: FieldType) -> int:
        match field_type:
            case FieldType.DOUBLE_WORD:
                return 2
            case FieldType.TRIPLE_WORD:
                return 3
            case _:
                return 1
