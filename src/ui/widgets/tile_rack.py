from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive

from ui.models import TileModel
from ui.widgets.draggable import Draggable
from ui.widgets.tile import Tile


class TileRack(Horizontal):
    BORDER_TITLE = 'Available letters'

    tiles: reactive[list[Tile]] = reactive(list, recompose=True)

    def get_selected(self) -> Tile | None:
        for tile in self.tiles:
            if tile.selected:
                return tile

        return None

    def update_tiles(self, tile_models: list[TileModel]) -> None:
        self.tiles = [Tile(tile_model) for tile_model in tile_models]

    def remove_tile(self, tile: Tile):
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
        self.tiles.sort(key=lambda x: x.region.x)
        self.mutate_reactive(TileRack.tiles)

        for tile in self.tiles:
            tile.styles.offset = (0, 0)
