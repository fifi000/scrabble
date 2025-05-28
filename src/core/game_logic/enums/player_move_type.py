from enum import Enum


class PlayerMoveType(Enum):
    PLACE_WORD = 0
    EXCHANGE = 1
    SKIP = 2