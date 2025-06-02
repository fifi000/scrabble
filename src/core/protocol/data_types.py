from __future__ import annotations

from typing import Self

from core.data_model import DataModel
from core.game_logic.board import Board
from core.game_logic.field import Field
from core.game_logic.player import Player
from core.game_logic.tile import Tile


class MessageData(DataModel):
    type: str
    data: dict | None = None


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

    @classmethod
    def from_tile(cls, tile: Tile) -> Self:
        return cls(
            id=tile.id,
            symbol=tile.symbol,
            points=tile.points,
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
            fields=[FieldData.from_field(field) for field in board.all_fields],
            rows=board.rows,
            columns=board.columns,
        )


class ClientData:
    class CreateRoomData(DataModel):
        room_number: int
        player_name: str

    class JoinRoomData(DataModel):
        room_number: int
        player_name: str

    class PlaceTilesData(DataModel):
        tile_ids: list[str]
        field_positions: list[tuple[int, int]]


# server data


class ServerData:
    class NewRoomData(DataModel):
        room_number: int
        player: PlayerData

    class JoinRoomData(DataModel):
        room_number: int
        player: list[PlayerData]

    class NewPlayerData(DataModel):
        player: PlayerData

    class NewGameData(DataModel):
        player: PlayerData
        current_player_id: str
        players: list[PlayerData]
        board: BoardData

    class NextTurnData(DataModel):
        player: PlayerData
        current_player_id: str
        players: list[PlayerData]
        board: BoardData
