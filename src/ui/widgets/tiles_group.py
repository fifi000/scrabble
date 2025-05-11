from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, HorizontalGroup
from textual import events

from ui.widgets.tile import Tile


class TilesGroup(Horizontal):
    BORDER_TITLE = 'Available letters'

    def __init__(self, tiles: list[Tile], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tiles = tiles

    def compose(self) -> ComposeResult:
        for tile in self.tiles:
            yield tile

    def on_click(self, event: events.Click) -> None:
        if isinstance(event.control, Tile):
            for tile in self.tiles:
                if tile == event.control:
                    tile.toggle_class('highlighted')
                else:
                    tile.remove_class('highlighted')
