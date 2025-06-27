import json
from abc import abstractmethod
from collections.abc import Collection, Iterable
from pathlib import Path
from typing import override

from ui.storage_manager import ConfigModel, SessionModel, StorageManager


class DesktopStorageManager(StorageManager):
    """A base class for desktop storage managers."""

    # --- Config ---

    @property
    @abstractmethod
    def storage_folder_path(self) -> Path:
        """Get the path to the storage location. None if web app."""

    @property
    @override
    def config_file_path(self) -> Path:
        """Get the path to the config file location"""
        file = self.storage_folder_path / self._config_file_name
        file.touch(exist_ok=True)

        return file

    @override
    def read_config(self) -> ConfigModel:
        """Read the configuration from storage."""
        json_text = self.config_file_path.read_text('utf8')

        try:
            config = json.loads(json_text) or {}
        except json.JSONDecodeError:
            config = {}

        assert isinstance(config, dict), f'Config must be a dict, got {type(config)}'

        return config

    @override
    def write_config(self, config: ConfigModel) -> None:
        """Write the configuration to storage."""
        json_text = json.dumps(config, indent=2, ensure_ascii=False)
        self.config_file_path.write_text(json_text, encoding='utf8')

    # --- Sessions ---

    @property
    @override
    def sessions_file_path(self) -> Path:
        """Get the path to the sessions location. None if web app."""
        file = self.storage_folder_path / self._sessions_file_name
        file.touch(exist_ok=True)

        return file

    @override
    def read_sessions(self) -> Collection[SessionModel]:
        """Read the sessions from storage."""
        json_text = self.sessions_file_path.read_text('utf8')

        try:
            dicts = json.loads(json_text) or []
        except json.JSONDecodeError:
            dicts = []

        sessions = [SessionModel.from_dict(d) for d in dicts]

        assert isinstance(sessions, list), (
            f'Sessions must be a list, got {type(sessions)}'
        )

        return sessions

    @override
    def write_sessions(self, sessions: Iterable[SessionModel]) -> None:
        """Write the sessions to storage."""
        dicts = [session.to_dict() for session in sessions]
        json_text = json.dumps(dicts, indent=2, ensure_ascii=False)
        self.sessions_file_path.write_text(json_text, encoding='utf8')

    @override
    def add_session(self, session: SessionModel) -> None:
        sessions = list(self.read_sessions())
        sessions.append(session)

        self.write_sessions(sessions)
