from abc import ABC
from typing import Any


class GameError(Exception, ABC):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)

        self.message = message
        self.details = details


class InternalGameError(GameError):
    def __init__(
        self, message: str | None = None, details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message
            if message is not None
            else 'An internal game error occurred.',
            details=details,
        )


class GameStartFailureError(GameError):
    def __init__(
        self, message: str | None = None, details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message if message is not None else 'Failed to start the game.',
            details=details,
        )


class GameAlreadyStartedError(GameError):
    def __init__(self) -> None:
        super().__init__('Game has already started.')


class GameNotInProgressError(GameError):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            message=message if message is not None else 'Game is not in progress.'
        )


class GameFinishedError(GameError):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            message=message if message is not None else 'Game has already finished.'
        )


class InvalidMoveError(GameError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, details=details)


class InvalidOperationError(GameError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, details=details)


class PlayerNotFoundError(GameError):
    def __init__(self, player_id: str) -> None:
        super().__init__(
            message='Player not found in the game.', details={'player_id': player_id}
        )


class PlayerAlreadyExistsError(GameError):
    def __init__(self, player_id: str, player_name: str) -> None:
        super().__init__(
            message='Player already exists in the game.',
            details={'player_id': player_id, 'player_name': player_name},
        )
