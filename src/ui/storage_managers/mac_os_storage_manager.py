from pathlib import Path
from typing import override

from ui.storage_managers.desktop_storage_manager import DesktopStorageManager


class MacOSStorageManager(DesktopStorageManager):
    """A storage manager for macOS."""

    @property
    @override
    def storage_folder_path(self) -> Path:
        path = Path.home() / 'Library' / 'Application Support' / self.app_name
        path.mkdir(parents=True, exist_ok=True)

        return path
