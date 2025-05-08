import uuid
from core.letter import Letter


class Player:
    def __init__(self, name: str) -> None:
        self.id: uuid.UUID = uuid.uuid4()
        self.name: str = name
        self.letters: list[Letter] = []
        self.scores: list[int]

    @property
    def score(self) -> int:
        return sum(self.scores)

    def __repr__(self) -> str:
        return f"{self.name} - {self.score}"
