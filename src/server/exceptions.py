from abc import ABC
from typing import Any


class ServerError(Exception, ABC):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)

        self.message = message
        self.details = details


class RoomNotFoundError(ServerError):
    def __init__(self, *, room_number: int) -> None:
        super().__init__(
            message=f'Room {room_number} does not exist.',
            details={'room_number': room_number},
        )


class NoActiveConnectionError(ServerError):
    def __init__(self) -> None:
        super().__init__('You are not connected to any room.')


class RoomAlreadyExistsError(ServerError):
    def __init__(self, *, room_number: int) -> None:
        super().__init__(
            message=f'Room {room_number} already exists.',
            details={'room_number': room_number},
        )


class NoActiveGameError(ServerError):
    def __init__(self, *, room_number: int) -> None:
        super().__init__(
            message=f'There is no active game in room {room_number}.',
            details={'room_number': room_number},
        )


class InvalidPlayerData(ServerError):
    def __init__(self, *, message: str, details: dict[str, Any]) -> None:
        super().__init__(message=message, details=details)


class DuplicatedConnectionError(ServerError):
    def __init__(self, *, player_name: str, room_number: int) -> None:
        super().__init__(
            message=f'You are already connected to this room as {player_name!r}.',
            details={'player_name': player_name, 'room_number': room_number},
        )


class PlayerNotInRoomError(ServerError):
    def __init__(self, *, room_number: int) -> None:
        super().__init__(
            message=f'Player not found in room {room_number}.',
            details={'room_number': room_number},
        )
