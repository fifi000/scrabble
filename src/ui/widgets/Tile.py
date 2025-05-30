from ui.widgets.draggable import Draggable


def _get_points_symbol(points: int) -> str:
    array = ['₀', '₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉']
    if not (0 <= points <= len(array)):
        raise Exception(f'Invalid number of points. {points=}')

    return array[points]


class Tile(Draggable):
    def __init__(self, symbol: str, points: int, *args, **kwargs) -> None:
        super().__init__(allow_vertical_drag=False, *args, **kwargs)

        self.symbol = symbol
        self.points = _get_points_symbol(points)

        self._enabled = True
        self._selected = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

        if not self._enabled:
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

    @property
    def text(self) -> str:
        return self.symbol + self.points

    def render(self) -> str:
        return self.text.center(self.size.width)

    def __repr__(self) -> str:
        return f'({self.symbol}{self.points})'
