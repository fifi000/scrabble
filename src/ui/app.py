import uuid
from textual.app import App

from core.enums.language import Language
from core.game import Game
from core.player import Player
from ui.screens.game_screen import GameScreen


class ScrabbleApp(App[None]):
    CSS_PATH = 'scrabble.tcss'
    TITLE = 'Scrabble'

    def on_mount(self) -> None:
        game = Game(Language.POLISH)

        players = [
            Player(uuid.uuid4(), 'Filip'),
            Player(uuid.uuid4(), 'Zuzia'),
        ]

        for player in players:
            game.add_player(player)

        self.push_screen(GameScreen(game, players[0].id))


if __name__ == '__main__':
    ScrabbleApp().run()
