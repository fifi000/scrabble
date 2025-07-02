from core.data_model import DataModel


class MessageData(DataModel):
    """Data model for messages sent between client and server."""

    type: str
    data: dict | None = None
