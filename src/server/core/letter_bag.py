import random
from typing import Generator
from core.enums.language import Language
from core.letter import Letter


class LetterBag:
    def __init__(self, language: Language) -> None:
        self.language: Language = language
        self._all_letters: list[Letter] = self._get_letters()
        self._available_letters: list[Letter] = self._all_letters[:]

    def _get_letters(self) -> list[Letter]:
        match self.language:
            case Language.POLISH:
                return list(LetterBag.polish_letters())
            case _:
                raise Exception('TODO')

    def scrabble(self, n: int) -> list[Letter]:
        if len(self._available_letters) < n:
            raise Exception("There is not enough letters in the bag")
        
        letters = random.sample(self._available_letters, n)

        for letter in letters:
            self._available_letters.remove(letter)

        return letters

    def exchange(self, letters: list[Letter]) -> list[Letter]:
        new_letters = self.scrabble(len(letters))

        self._available_letters.extend(letters)

        return new_letters


    @staticmethod
    def polish_letters() -> Generator[Letter, None, None]:
        foo = {
            0: [('', 2)],
            1: [('A', 9), ('E', 7), ('I', 8), ('N', 5), ('O', 6), ('R', 4), ('S', 4), ('W', 4), ('Z', 5)],
            2: [('C', 3), ('D', 3), ('K', 3), ('L', 3), ('M', 3), ('P', 3), ('T', 3), ('Y', 4)],
            3: [('B', 2), ('G', 2), ('H', 2), ('J', 2), ('Ł', 2), ('U', 2)],
            5: [('Ą', 1), ('Ę', 1), ('F', 1), ('Ó', 1), ('Ś', 1), ('Ż', 1)],
            6: [('Ć', 1)],
            7: [('Ń', 1)],
            9: [('Ź', 1)],
        }

        for points, collection in foo.items():
            for symbol, count in collection:
                for _ in range(count):
                    yield Letter(symbol, points)


