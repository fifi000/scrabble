import json
from abc import abstractmethod
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
        config = json.loads(json_text) or {}

        assert isinstance(config, dict), f'Config must be a dict, got {type(config)}'

        return config

    @override
    def write_config(self, config: ConfigModel) -> None:
        """Write the configuration to storage."""
        json_text = json.dumps(config, indent=2, ensure_ascii=False)
        self.config_file_path.write_text(json_text, encoding='utf8')

    # --- Sessions ---

    @property
    @abstractmethod
    def sessions_file_path(self) -> Path:
        """Get the path to the sessions location. None if web app."""

    @override
    def read_sessions(self) -> SessionModel:
        """Read the sessions from storage."""
        json_text = self.sessions_file_path.read_text('utf8')
        config = json.loads(json_text) or {}

        assert isinstance(config, dict), f'Sessions must be a dict, got {type(config)}'

        return config

    @override
    def write_sessions(self, sessions: SessionModel) -> None:
        """Write the sessions to storage."""
        json_text = json.dumps(sessions, indent=2, ensure_ascii=False)
        self.config_file_path.write_text(json_text, encoding='utf8')
