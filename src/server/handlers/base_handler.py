from abc import ABC

from server.room_manager import RoomManager


class BaseHandler(ABC):
    def __init__(self, room_manager: RoomManager) -> None:
        self.room_manager = room_manager
