from collections.abc import Iterator
from typing import override

from textual import events, on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive

from ui.models.tile_model import TileModel
from ui.widgets.draggable import Draggable
from ui.widgets.tile import Tile


class TileRack(Horizontal):
    BORDER_TITLE = 'Available letters'

    tiles: reactive[list[Tile]] = reactive(list, recompose=True)

    def get_selected(self) -> Iterator[Tile]:
        for tile in self.tiles:
            if tile.selected:
                yield tile

    def update_tiles(self, tile_models: list[TileModel]) -> None:
        self.tiles = [Tile(tile_model) for tile_model in tile_models]

    def remove_tile(self, tile: Tile):
        self.tiles.remove(tile)
        self.mutate_reactive(TileRack.tiles)

    @override
    def compose(self) -> ComposeResult:
        for tile in self.tiles:
            yield tile

    def on_click(self, event: events.Click) -> None:
        if isinstance(event.control, Tile):
            # multiselection
            if event.ctrl:
                event.control.toggle_selected()
            # at most one can be selected
            else:
                for tile in self.tiles:
                    if tile == event.control:
                        tile.toggle_selected()
                    else:
                        tile.selected = False

    @on(Draggable.DragEnded)
    def handle_drag_ended(self) -> None:
        # reorder tiles
        self.tiles.sort(key=lambda x: x.region.x)
        self.mutate_reactive(TileRack.tiles)

        for tile in self.tiles:
            tile.styles.offset = (0, 0)
