from typing import Any, override

from textual.app import App

from ui.storage_manager import ConfigModel, SessionModel, StorageManager


class WebStorageManager(StorageManager):
    """A base class for web storage managers."""

    def __init__(self, app: App[Any], app_name: str) -> None:
        super().__init__(app, app_name)

        self._config: ConfigModel = {}
        self._sessions: SessionModel = {}

    # --- Config ---

    @property
    @override
    def storage_folder_path(self) -> None:
        """Always None."""
        return None

    @property
    @override
    def config_file_path(self) -> None:
        """Always None"""
        return None

    @override
    def read_config(self) -> ConfigModel:
        """Read the configuration from storage."""
        return self._config

    @override
    def write_config(self, config: ConfigModel) -> None:
        """Write the configuration to storage."""
        self._config = config

    # --- Sessions ---

    @property
    def sessions_file_path(self) -> None:
        """Always None"""
        return None

    @override
    def read_sessions(self) -> SessionModel:
        """Read the sessions from storage."""
        return self._sessions

    @override
    def write_sessions(self, sessions: SessionModel) -> None:
        """Write the sessions to storage."""
        self._sessions = sessions
