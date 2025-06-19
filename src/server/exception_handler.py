import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import overload

from websockets import ServerConnection

from core import tools
from core.exceptions.game import (
    GameAlreadyStartedError,
    GameError,
    GameFinishedError,
    GameNotInProgressError,
    GameStartFailureError,
    InvalidMoveError,
    InvalidOperationError,
    PlayerAlreadyExistsError,
    PlayerNotFoundError,
)
from core.protocol.error_codes import ErrorCode
from core.protocol.errors import ErrorData
from server.communication import send_error
from server.exceptions import (
    DuplicatedConnectionError,
    InvalidPlayerData,
    NoActiveConnectionError,
    NoActiveGameError,
    PlayerNotInRoomError,
    RoomAlreadyExistsError,
    RoomNotFoundError,
    ServerError,
)

logger = logging.getLogger(__name__)


def handle_exception[**P](
    func: Callable[P, Awaitable[None]],
) -> Callable[P, Awaitable[None]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        websocket = tools.find_arg(args, kwargs, ServerConnection)
        try:
            await func(*args, **kwargs)
        except GameError as e:
            logger.warning(
                msg=f'{GameError.__name__!r} in {func.__name__!r}: {e.message!r}',
                extra={
                    'exception_type': type(e).__name__,
                    'details': e.details,
                    'handler': func.__name__,
                },
            )
            await _exception_handler(websocket, e)
        except ServerError as e:
            logger.warning(
                msg=f'{ServerError.__name__!r} in {func.__name__!r}: {e.message!r}',
                extra={
                    'exception_type': type(e).__name__,
                    'details': e.details,
                    'handler': func.__name__,
                },
            )
            await _exception_handler(websocket, e)
        except Exception as e:
            logger.error(
                msg=f'Unexpected error in {func.__name__!r}: {e}',
                extra={
                    'exception_type': type(e).__name__,
                    'handler': func.__name__,
                },
                exc_info=True,
            )
            await _exception_handler(websocket, e)

    return wrapper


async def _exception_handler(websocket: ServerConnection, exception: Exception) -> None:
    error_data = _get_error_data(exception)

    await send_error(
        websocket,
        code=error_data.code,
        message=error_data.message,
        details=error_data.details,
    )


def _get_error_data(exception: Exception) -> ErrorData:
    match exception:
        case GameError():
            return ErrorData(
                code=_get_error_code(exception),
                message=exception.message,
                details=exception.details,
            )

        case ServerError():
            return ErrorData(
                code=_get_error_code(exception),
                message=exception.message,
                details=exception.details,
            )

        case _:
            return ErrorData(
                code=ErrorCode.INTERNAL_ERROR,
                message='An internal server error occurred.',
                details=None,
            )


@overload
def _get_error_code(exception: GameError) -> ErrorCode: ...


@overload
def _get_error_code(exception: ServerError) -> ErrorCode: ...


def _get_error_code(exception: GameError | ServerError) -> ErrorCode:
    match exception:
        # --- GameError ---
        case GameStartFailureError():
            return ErrorCode.GAME_START_FAILURE
        case GameAlreadyStartedError():
            return ErrorCode.GAME_ALREADY_STARTED
        case GameNotInProgressError():
            return ErrorCode.GAME_NOT_IN_PROGRESS
        case GameFinishedError():
            return ErrorCode.GAME_FINISHED
        case InvalidMoveError():
            return ErrorCode.INVALID_MOVE
        case InvalidOperationError():
            return ErrorCode.INVALID_OPERATION
        case PlayerNotFoundError():
            return ErrorCode.PLAYER_NOT_FOUND
        case PlayerAlreadyExistsError():
            return ErrorCode.PLAYER_ALREADY_EXISTS
        case GameError():
            if type(exception) is GameError:
                return ErrorCode.GAME_ERROR
            raise RuntimeError(
                f'Unhandled {GameError.__name__!r} type: {type(exception).__name__!r}'
            )

        # --- ServerError ---
        case RoomNotFoundError():
            return ErrorCode.ROOM_NOT_FOUND
        case NoActiveConnectionError():
            return ErrorCode.NO_ACTIVE_CONNECTION
        case RoomAlreadyExistsError():
            return ErrorCode.ROOM_ALREADY_EXISTS
        case NoActiveGameError():
            return ErrorCode.NO_ACTIVE_GAME
        case InvalidPlayerData():
            return ErrorCode.INVALID_PLAYER_DATA
        case PlayerNotInRoomError():
            return ErrorCode.PLAYER_NOT_IN_ROOM
        case DuplicatedConnectionError():
            return ErrorCode.DUPLICATED_CONNECTION
        case ServerError():
            if type(exception) is ServerError:
                return ErrorCode.SERVER_ERROR
            raise RuntimeError(
                f'Unhandled {ServerError.__name__!r} type: {type(exception).__name__!r}'
            )
