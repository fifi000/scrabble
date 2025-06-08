from enum import IntEnum


class GameState(IntEnum):
    GAME_NOT_STARTED = 0
    GAME_IN_PROGRESS = 1
    GAME_FINISHED = 2


class FieldType(IntEnum):
    STANDARD = 0

    # letter bonuses
    DOUBLE_LETTER = 1
    TRIPLE_LETTER = 2

    # word bonuses
    DOUBLE_WORD = 3
    TRIPLE_WORD = 4

    def is_bonus(self) -> bool:
        return self.value != FieldType.STANDARD

    def is_letter_bonus(self) -> bool:
        return self.value in {FieldType.DOUBLE_LETTER, FieldType.TRIPLE_LETTER}

    def is_word_bonus(self) -> bool:
        return self.value in {FieldType.DOUBLE_WORD, FieldType.TRIPLE_WORD}


class Language(IntEnum):
    POLISH = 0
    ENGLISH = 1
    GERMAN = 2


class PlayerMoveType(IntEnum):
    PLACE_WORD = 0
    EXCHANGE = 1
    SKIP = 2
