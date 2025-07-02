from os import getenv
from pathlib import Path
from typing import override

from ui.storage_managers.desktop_storage_manager import DesktopStorageManager


class LinuxStorageManager(DesktopStorageManager):
    """A storage manager for Linux."""

    @property
    @override
    def storage_folder_path(self) -> Path:
        if base := getenv('XDG_DATA_HOME'):
            path = Path(base) / self.app_name
        else:
            path = Path.home() / '.local' / 'share' / self.app_name

        path.mkdir(parents=True, exist_ok=True)

        return path
