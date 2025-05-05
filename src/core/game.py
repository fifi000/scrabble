from __future__ import annotations
from core.board import Board
from core.enums.language import Language
from core.letter import Letter
from core.letter_bag import LetterBag
from core.player import Player
from core.position import Position
from functools import wraps


class Game:
    def __init__(self, players: list[Player], language: Language) -> None:
        self.players: list[Player] = players
        self.language = language
        self.letter_bag = LetterBag(language)
        self.board = Board()
        self.move = 0

        for player in self.players:
            player.letters = self.letter_bag.scrabble(7)

    @property
    def current_player(self) -> Player:
        return self.players[self.move % len(self.players)]

    def can_play(self) -> bool:
        return True

    def is_valid_word_placement(self, letter_positions: list[tuple[Position, Letter]]) -> bool:
        return True

        for position, letter in letter_positions:
            if not self.board.get_field(position).is_empty:
                return False        
        
        return True

    # 
    # player available moves
    # 

    def _check_player(self, player: Player) -> None:
        if player != self.current_player:
            if player not in self.players:
                raise Exception('There is no player in game corresponding to provided player.')
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
    def exchange_letters(self, player: Player, letters: list[Letter]) -> None:
        new_letters = self.letter_bag.exchange(letters)
        
        for letter in letters:
            player.letters.remove(letter)

        player.letters.extend(new_letters)

    @player_move
    def place_letters(self, player: Player, letter_positions: list[tuple[Position, Letter]]) -> None:
        if not self.is_valid_word_placement(letter_positions):
            raise Exception('Given move is not valid.')            

        self.board.place_letters(letter_positions)

        for position, letter in letter_positions:
            player.letters.remove(letter)

        new_letters = self.letter_bag.scrabble(len(letter_positions))
        player.letters.extend(new_letters)
