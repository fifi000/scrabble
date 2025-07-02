from abc import ABC, abstractmethod
from collections.abc import Collection, Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

from textual.app import App

from core.data_model import DataModel

ConfigModel = dict[str, Any]


class SessionModel(DataModel):
    id: str
    room_number: int
    uri: str
    player_name: str
    datetime: str = datetime.now().isoformat()


class StorageManager(ABC):
    """A base class for storage managers."""

    def __init__(self, app: App[Any], app_name: str) -> None:
        self._app = app

        if not app_name:
            raise ValueError(f'{app_name!r} must be provided')

        self._app_name = app_name

        self._config_file_name = 'config.json'
        self._sessions_file_name = 'sessions.json'

    @property
    def app_name(self) -> str:
        return self._app_name

    @property
    @abstractmethod
    def storage_folder_path(self) -> Path | None:
        """Get the path to the storage location. None if web app."""

    # --- Config ---

    @property
    @abstractmethod
    def config_file_path(self) -> Path | None:
        """Get the path to the config file location. None if web app."""

    @abstractmethod
    def read_config(self) -> ConfigModel:
        """Read the configuration from storage."""

    @abstractmethod
    def write_config(self, config: ConfigModel) -> None:
        """Write the configuration to storage."""

    # --- Sessions ---

    @property
    @abstractmethod
    def sessions_file_path(self) -> Path | None:
        """Get the path to the sessions location. None if web app."""

    @abstractmethod
    def read_sessions(self) -> Collection[SessionModel]:
        """Read the sessions from storage."""

    @abstractmethod
    def write_sessions(self, sessions: Iterable[SessionModel]) -> None:
        """Write the sessions to storage."""

    @abstractmethod
    def add_session(self, session: SessionModel) -> None:
        """Add a session to storage."""
