from enum import Enum


class FieldType(Enum):
    STANDARD = 0

    # letter bonuses
    DOUBLE_LETTER = 1
    TRIPPLE_LETTER = 2

    # word bonuses
    DOUBLE_WORD = 3
    TRIPPLE_WORD = 4

    def is_bonus(self) -> bool:
        return self.value != FieldType.STANDARD
