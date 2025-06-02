from core.data_model import DataModel


class MessageData(DataModel):
    type: str
    data: dict | None = None
