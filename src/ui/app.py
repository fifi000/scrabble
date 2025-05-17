import uuid
from textual.app import App

from core.enums.language import Language
from core.game import Game
from ui.screens.game_screen import GameScreen
from ui.screens.start_menu_screen import StartMenuScreen


class ScrabbleApp(App[None]):
    CSS_PATH = 'scrabble.tcss'
    TITLE = 'Scrabble'

    def on_mount(self) -> None:
        self.push_screen(StartMenuScreen())

    def on_start_menu_screen_join_room(self, message: StartMenuScreen.JoinRoom) -> None:
        self.switch_screen(GameScreen(Game(Language.POLISH), uuid.uuid4()))

    def on_start_menu_screen_create_room(
        self, message: StartMenuScreen.CreateRoom
    ) -> None:
        self.switch_screen(GameScreen(Game(Language.POLISH), uuid.uuid4()))


if __name__ == '__main__':
    ScrabbleApp().run()
