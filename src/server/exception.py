class ServerError(Exception):
    pass


# --- room errors ---


class RoomNotFoundError(ServerError):
    def __init__(self, room_number: int) -> None:
        super().__init__(f'Room {room_number} not found.')
        self.room_number = room_number


class RoomAlreadyExistsError(ServerError):
    def __init__(self, room_number: int) -> None:
        super().__init__(f'Room {room_number} already exists.')
        self.room_number = room_number


#  --- player errors ---


class PlayerAlreadyExistsError(ServerError):
    pass


class PlayerNotFoundError(ServerError):
    pass


class PlayerNotInRoomError(ServerError):
    pass


# --- game errors ---


class CouldNotStartGameError(ServerError):
    pass


class GameAlreadyStartedError(ServerError):
    pass


class GameNotStartedError(ServerError):
    pass


class InvalidMoveError(ServerError):
    pass


# --- message errors ---


class InvalidMessageError(ServerError):
    pass
