from textual.app import ComposeResult
from textual.containers import Horizontal
from textual import events
from textual.reactive import reactive

from ui.widgets.draggable import Draggable
from ui.widgets.tile import Tile


class TileRack(Horizontal):
    BORDER_TITLE = 'Available letters'

    tiles: reactive[list[Tile]] = reactive(list, recompose=True)

    def __init__(self, tiles: list[Tile], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tiles = tiles

    def get_selected(self) -> Tile | None:
        for tile in self.tiles:
            if tile.selected:
                return tile

        return None

    def remove(self, tile):
        self.tiles.remove(tile)
        self.mutate_reactive(TileRack.tiles)

    def compose(self) -> ComposeResult:
        for tile in self.tiles:
            yield tile

    def on_click(self, event: events.Click) -> None:
        if isinstance(event.control, Tile):
            for tile in self.tiles:
                if tile == event.control:
                    tile.selected = not tile.selected
                else:
                    tile.selected = False

    def on_draggable_drag_ended(self, message: Draggable.DragEnded) -> None:
        # reorder tiles
        self.tiles = list(sorted(self.tiles, key=lambda x: x.region.x))
        for tile in self.tiles:
            tile.styles.offset = (0, 0)
