from abc import ABC
from typing import Any


class GameError(Exception, ABC):
    """Base class for all game-related exceptions.

    Attributes:
        message (str): A description of the error.
        details (dict[str, Any] | None): Optional additional details about the error.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)

        self.message = message
        self.details = details


class InternalGameError(GameError):
    """Raised when an internal game error occurs that should not happen under normal circumstances.

    Attributes:
        message (str): A description of the error, defaults to a generic internal error message.
        details (dict[str, Any] | None): Optional additional details about the error.
    """

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
    """Raised when the game fails to start.

    Attributes:
        message (str): A description of the error, defaults to a generic game start failure message.
        details (dict[str, Any] | None): Optional additional details about the error.
    """

    def __init__(
        self, message: str | None = None, details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message if message is not None else 'Failed to start the game.',
            details=details,
        )


class GameAlreadyStartedError(GameError):
    """Raised when an operation is attempted on a game that has already started."""

    def __init__(self) -> None:
        super().__init__('Cannot start the game: Game has already started.')


class GameNotInProgressError(GameError):
    """Raised when an operation is attempted on a game that is not currently in progress.

    Attributes:
        message (str | None): A description of the error.
    """

    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            message=message if message is not None else 'Game is not in progress.'
        )


class GameFinishedError(GameError):
    """Raised when an operation is attempted on a game that has already finished.

    Attributes:
        message (str | None): A description of the error.
    """

    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            message=message if message is not None else 'Game has already finished.'
        )


class InvalidMoveError(GameError):
    """Raised when an invalid player move is attempted in the game.

    Attributes:
        message (str): A description of the error.
        details (dict[str, Any] | None): Optional additional details about the error.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, details=details)


class InvalidOperationError(GameError):
    """Raised when an invalid operation is attempted in the game.

    Attributes:
        message (str): A description of the error.
        details (dict[str, Any] | None): Optional additional details about the error.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, details=details)


class PlayerNotFoundError(GameError):
    """Raised when a player is not found in the game.

    Attributes:
        player_id (str): The ID of the player that was not found.
    """

    def __init__(self, player_id: str) -> None:
        super().__init__(
            message='Player not found in the game.', details={'player_id': player_id}
        )


class PlayerAlreadyExistsError(GameError):
    """Raised when a player with the same ID or name already exists in the game.

    Attributes:
        player_id (str): The ID of the player that already exists.
        player_name (str): The name of the player that already exists.
    """

    def __init__(self, player_id: str, player_name: str) -> None:
        super().__init__(
            message='Player already exists in the game.',
            details={'player_id': player_id, 'player_name': player_name},
        )
