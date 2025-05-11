from core.tile import Tile as GameTile

from textual.widgets import Static
from textual.reactive import reactive

from ui.widgets.draggable import Draggable


def _get_points_symbol(points: int) -> str:
    array = ['₀', '₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉']
    if not (0 <= points <= len(array)):
        raise Exception(f'Invalid number of points. {points=}')

    return array[points]


class Tile(Draggable):
    text = reactive('')

    def __init__(self, game_tile: GameTile, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.text = ' ' + game_tile.symbol + _get_points_symbol(game_tile.points)
        self.game_tile = game_tile

    def render(self) -> str:
        return self.text
