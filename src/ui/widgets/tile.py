from typing import override

from ui.models import TileModel
from ui.widgets.draggable import Draggable


def _get_points_symbol(points: int) -> str:
    array = ['₀', '₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉']
    if not (0 <= points <= len(array)):
        raise Exception(f'Invalid number of points. {points=}')

    return array[points]


class Tile(Draggable):
    def __init__(self, model: TileModel, *args, **kwargs) -> None:
        super().__init__(allow_vertical_drag=False, *args, **kwargs)

        self.model = model

        self._enabled = True
        self._selected = False

    @property
    def symbol(self) -> str:
        return self.model.symbol

    @property
    def points(self) -> str:
        return _get_points_symbol(self.model.points)

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

        if self._enabled:
            self.remove_class('disabled')
        else:
            self.add_class('disabled')
            self.selected = False

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value: bool) -> None:
        self._selected = self.enabled and value
        if self._selected:
            self.add_class('highlighted')
        else:
            self.remove_class('highlighted')

    def toggle_selected(self) -> None:
        self.selected = not self.selected

    @property
    def text(self) -> str:
        return self.symbol + self.points

    @override
    def render(self) -> str:
        return self.text.center(self.size.width)

    def __repr__(self) -> str:
        return f'({self.symbol}{self.points})'
