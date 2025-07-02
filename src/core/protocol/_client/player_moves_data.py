from core.protocol.data_types.tile_data import TileData
from core.protocol.sessionable import Sessionable


class PlaceTilesData(Sessionable):
    """Data for placing tiles on the board."""

    tiles_data: list[TileData]


class ExchangeTilesData(Sessionable):
    """Data for exchanging tiles."""

    tiles_data: list[TileData]


class SkipTurnData(Sessionable):
    """Data for skipping a turn."""
