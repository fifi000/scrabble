from enum import StrEnum


class ErrorCode(StrEnum):
    """Enumeration of error codes used in the application."""

    # --- game ---
    GAME_ERROR = 'game_error'
    GAME_START_FAILURE = 'game_start_failure'
    GAME_ALREADY_STARTED = 'game_already_started'
    GAME_NOT_IN_PROGRESS = 'game_not_in_progress'
    GAME_FINISHED = 'game_finished'
    INVALID_MOVE = 'invalid_move'
    INVALID_OPERATION = 'invalid_operation'
    PLAYER_NOT_FOUND = 'player_not_found'
    PLAYER_ALREADY_EXISTS = 'player_already_exists'

    # --- server ---
    SERVER_ERROR = 'server_error'
    ROOM_NOT_FOUND = 'room_not_found'
    NO_ACTIVE_CONNECTION = 'no_active_connection'
    ROOM_ALREADY_EXISTS = 'room_already_exists'
    NO_ACTIVE_GAME = 'no_active_game'
    INVALID_PLAYER_DATA = 'invalid_player_data'
    PLAYER_NOT_IN_ROOM = 'player_not_in_room'
    DUPLICATED_CONNECTION = 'duplicated_connection'
    INTERNAL_ERROR = 'internal_error'

    #
    INVALID_MESSAGE_TYPE = 'invalid_message_type'
