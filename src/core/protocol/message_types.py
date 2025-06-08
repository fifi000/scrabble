from enum import StrEnum


class ClientMessageType(StrEnum):
    # server actions
    JOIN_ROOM = 'join_room'
    START_GAME = 'start_game'
    CREATE_ROOM = 'create_room'
    # game moves
    PLACE_TILES = 'place_tiles'
    EXCHANGE_TILES = 'exchange_tiles'
    SKIP_TURN = 'skip_turn'


class ServerMessageType(StrEnum):
    ERROR = 'error'
    NEW_ROOM_CREATED = 'new_room_created'
    NEW_PLAYER = 'new_player'
    JOIN_ROOM = 'join_room'
    NEW_GAME = 'new_game'
    NEXT_TURN = 'next_turn'
    NEW_TILES = 'new_tiles'
