from typing import Any

from core.data_model import DataModel


class ErrorData(DataModel):
    """Data model for error messages sent from the server to the client."""

    code: str
    message: str
    details: dict[str, Any] | None = None
