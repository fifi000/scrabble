from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, HorizontalGroup
from textual import events
from textual.css.scalar import ScalarOffset

from ui.widgets.draggable import Draggable
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

    def on_draggable_drag_ended(self, message: Draggable.DragEnded) -> None:
        # reorder tiles
        self.tiles = list(sorted(self.tiles, key=lambda x: x.region.x))
        for tile in self.tiles:
            tile.styles.offset = (0, 0)
        self.refresh(repaint=True, layout=True, recompose=True)
