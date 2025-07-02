from abc import ABC

from core.data_model import DataModel


class Sessionable(DataModel, ABC):
    session_id: str
