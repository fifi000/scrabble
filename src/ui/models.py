from __future__ import annotations
from typing import Self

from core.data_model import DataModel
from core.game_logic.enums.field_type import FieldType
from core.protocol.data_types import BoardData, FieldData, PlayerData, TileData


class PlayerModel(DataModel):
    id: str
    name: str
    tiles: list[TileModel]
    scores: list[int]

    @classmethod
    def empty(cls) -> PlayerModel:
        return cls(id='', name='', tiles=[], scores=[])

    @classmethod
    def from_player_data(cls, player_data: PlayerData) -> Self:
        return cls(
            id=player_data.id,
            name=player_data.name,
            tiles=[TileModel.from_tile_data(tile) for tile in player_data.tiles or []],
            scores=player_data.scores or [],
        )

    def to_player_data(self) -> PlayerData:
        player_data = PlayerData(
            id=self.id,
            name=self.name,
        )

        if self.tiles is not None:
            player_data.tiles = [tile.to_tile_data() for tile in self.tiles]

        return player_data


class FieldModel(DataModel):
    row: int
    column: int
    type: FieldType
    tile: TileModel | None = None

    @classmethod
    def from_field_data(cls, field_data: FieldData) -> Self:
        field_model = cls(
            row=field_data.row,
            column=field_data.column,
            type=FieldType(field_data.type),
        )

        if field_data.tile is not None:
            field_model.tile = TileModel.from_tile_data(field_data.tile)

        return field_model

    def to_field_data(self) -> FieldData:
        field_data = FieldData(
            row=self.row,
            column=self.column,
            type=self.type.value,
        )

        if self.tile:
            field_data.tile = self.tile.to_tile_data()

        return field_data


class TileModel(DataModel):
    id: str
    symbol: str
    points: int

    @classmethod
    def from_tile_data(cls, tile_data: TileData) -> Self:
        return cls(
            id=tile_data.id,
            symbol=tile_data.symbol,
            points=tile_data.points,
        )

    def to_tile_data(self) -> TileData:
        return TileData(
            id=self.id,
            symbol=self.symbol,
            points=self.points,
        )


class BoardModel(DataModel):
    rows: int
    columns: int
    fields: list[FieldModel]

    @classmethod
    def form_board_data(cls, board_data: BoardData) -> BoardModel:
        return cls(
            rows=board_data.rows,
            columns=board_data.columns,
            fields=[FieldModel.from_field_data(field) for field in board_data.fields],
        )

    def to_board_data(self) -> BoardData:
        return BoardData(
            rows=self.rows,
            columns=self.columns,
            fields=[field.to_field_data() for field in self.fields],
        )
