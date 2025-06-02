from enum import StrEnum


# --- client types


class ClientMessageType(StrEnum):
    JOIN_ROOM = 'join_room'
    START_GAME = 'start_game'
    PLACE_TILES = 'place_tiles'
    CREATE_ROOM = 'create_room'


# --- server types ---


class ServerMessageType(StrEnum):
    ERROR = 'error'
    NEW_ROOM_CREATED = 'new_room_created'
    NEW_PLAYER = 'new_player'
    JOIN_ROOM = 'join_room'
    NEW_GAME = 'new_game'
    NEXT_TURN = 'next_turn'
    NEW_TILES = 'new_tiles'


class ServerErrorCode(StrEnum):
    # message
    INVALID_MESSAGE_TYPE = 'invalid_message_type'
    INVALID_DATA = 'invalid_data'
    MISSING_DATA = 'missing_data'

    # room
    ROOM_NOT_FOUND = 'room_not_found'
    ROOM_ALREADY_EXISTS = 'room_already_exists'

    # player
    PLAYER_NOT_FOUND = 'player_not_found'
    DIFFERENT_PLAYER_TURN = 'different_player_turn'
    INVALID_NAME = 'invalid_name'

    # game
    GAME_START_FAILED = 'game_start_failed'
    GAME_NOT_STARTED = 'game_not_started'
    GAME_ALREADY_STARTED = 'game_already_started'
    INVALID_MOVE = 'invalid_move'
