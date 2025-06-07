from typing import Any

from core.data_model import DataModel


class ErrorData(DataModel):
    code: str
    message: str
    details: dict[str, Any] | None = None
