from enum import IntEnum


class GameState(IntEnum):
    """Enumeration of possible game states."""

    GAME_NOT_STARTED = 0
    GAME_IN_PROGRESS = 1
    GAME_FINISHED = 2


class FieldType(IntEnum):
    """Type of a field on the game board."""

    STANDARD = 0

    # letter bonuses
    DOUBLE_LETTER = 1
    TRIPLE_LETTER = 2

    # word bonuses
    DOUBLE_WORD = 3
    TRIPLE_WORD = 4

    @property
    def is_bonus(self) -> bool:
        """Check if the field is a bonus field."""
        return self.value != FieldType.STANDARD

    @property
    def is_letter_bonus(self) -> bool:
        """Check if the field is a letter bonus field."""
        return self.value in {FieldType.DOUBLE_LETTER, FieldType.TRIPLE_LETTER}

    @property
    def is_word_bonus(self) -> bool:
        """Check if the field is a word bonus field."""
        return self.value in {FieldType.DOUBLE_WORD, FieldType.TRIPLE_WORD}


class Language(IntEnum):
    """Enumeration of supported languages."""

    POLISH = 0
    ENGLISH = 1
    GERMAN = 2


class PlayerMoveType(IntEnum):
    """Enumeration of player move types."""

    PLACE_WORD = 0
    EXCHANGE = 1
    SKIP = 2
