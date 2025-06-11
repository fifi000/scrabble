from __future__ import annotations

from typing import Self

from core.data_model import DataModel
from core.game.objects.board import Board
from core.game.objects.field import Field
from core.game.objects.player import Player
from core.game.objects.tile import Tile
from core.game.types import Position


class PlayerData(DataModel):
    id: str
    name: str
    tiles: list[TileData] | None = None
    scores: list[int] | None = None

    @classmethod
    def from_player(cls, player: Player, with_tiles: bool = False) -> Self:
        obj = cls(
            id=player.id,
            name=player.name,
            scores=player.scores,
        )

        if with_tiles:
            obj.tiles = [TileData.from_tile(tile) for tile in player.tiles]

        return obj


class TileData(DataModel):
    id: str
    symbol: str
    points: int
    position: Position | None = None

    @classmethod
    def from_tile(cls, tile: Tile, position: Position | None = None) -> Self:
        return cls(
            id=tile.id,
            symbol=tile.symbol,
            points=tile.points,
            position=position,
        )


class FieldData(DataModel):
    row: int
    column: int
    type: int
    tile: TileData | None = None

    @classmethod
    def from_field(cls, field: Field) -> Self:
        obj = cls(
            row=field.row,
            column=field.column,
            type=field.type.value,
        )

        if field.tile:
            obj.tile = TileData.from_tile(field.tile)

        return obj


class BoardData(DataModel):
    rows: int
    columns: int
    fields: list[FieldData]

    @classmethod
    def from_board(cls, board: Board) -> Self:
        return cls(
            fields=[FieldData.from_field(field) for field in board.get_fields()],
            rows=board.rows,
            columns=board.columns,
        )
