
from core.enums.language import Language
from core.game import Game
from core.player import Player
from core.position import Position


def main() -> None:
    players = [
        Player('Filip'),
        Player('Zuzia'),
    ]
    
    game = Game(players, Language.POLISH)

    while True:
        current_player = game.current_player

        print(f"\n[# {game.move}] It's player {current_player.name} turn!")
        current_letters = ' '.join([letter.symbol for letter in current_player.letters])
        print(f'Current letters: "{current_letters}"')

        word = input('Word: ').strip().upper()

        available_letters = current_player.letters.copy()
        letters = []

        for char in word:
            letter = next((x for x in available_letters if x.symbol == char))
            letters.append(letter)

        game.place_letters(current_player, [(Position(0, 0), letter) for letter in letters])


if __name__ == '__main__':    
    main()
