from os import getenv
from pathlib import Path
from typing import override

from ui.storage_managers.desktop_storage_manager import DesktopStorageManager


class WindowsStorageManager(DesktopStorageManager):
    """A storage manager for Windows."""

    @property
    @override
    def storage_folder_path(self) -> Path:
        if base := getenv('APPDATA'):
            path = Path(base) / self.app_name
        else:
            path = Path.home() / 'AppData' / 'Roaming' / self.app_name

        path.mkdir(parents=True, exist_ok=True)

        return path
