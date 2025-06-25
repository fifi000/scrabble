from enum import StrEnum


class ClientMessageType(StrEnum):
    # server actions
    JOIN_ROOM = 'join_room'
    START_GAME = 'start_game'
    CREATE_ROOM = 'create_room'
    REJOIN = 'rejoin'
    # game moves
    PLACE_TILES = 'place_tiles'
    EXCHANGE_TILES = 'exchange_tiles'
    SKIP_TURN = 'skip_turn'


class ServerMessageType(StrEnum):
    ERROR = 'error'
    NEW_ROOM_CREATED = 'new_room_created'
    NEW_PLAYER = 'new_player'
    PLAYER_REJOIN = 'player_rejoin'
    JOIN_ROOM = 'join_room'
    REJOIN_ROOM = 'rejoin_room'
    NEW_GAME = 'new_game'
    REJOIN_GAME = 'rejoin_game'
    NEXT_TURN = 'next_turn'
    NEW_TILES = 'new_tiles'
