from textual.app import App

from core.enums.language import Language
from core.game import Game as CoreGame
from core.player import Player
from ui.screens.game import Game


class Scrabble(App[None]):
    CSS_PATH = 'scrabble.tcss'
    TITLE = 'Scrabble'

    def on_mount(self) -> None:
        players = [
            Player('Filip'),
            Player('Zuzia'),
        ]

        game = CoreGame(players, Language.POLISH)
        self.push_screen(Game(game, players[0].id))


if __name__ == '__main__':
    Scrabble().run()
