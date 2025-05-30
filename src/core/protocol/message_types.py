from enum import StrEnum


class ServerMessageType(StrEnum):
    NEW_ROOM_CREATED = 'new_room_created'
    NEW_PLAYER = 'new_player'
    JOIN_ROOM = 'join_room'
    GAME_STARTED = 'game_started'
    TILES_PLACED = 'tiles_placed'
    NEW_TILES = 'new_tiles'


class ClientMessageType(StrEnum):
    JOIN_ROOM = 'join_room'
    START_GAME = 'start_game'
    PLACE_TILES = 'place_tiles'
    CREATE_ROOM = 'create_room'
