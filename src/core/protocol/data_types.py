from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields, is_dataclass
from types import UnionType
from typing import Type, TypeVar, get_args, get_type_hints

from core.game_logic.board import Board
from core.game_logic.field import Field
from core.game_logic.player import Player
from core.game_logic.tile import Tile

T = TypeVar('T', bound='BaseData')


@dataclass
class BaseData:
    @classmethod
    def from_json(cls: Type[T], json_string: str) -> T:
        return cls(**json.loads(json_string))

    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        fieldtypes = get_type_hints(cls)
        init_kwargs = {}

        for field in fields(cls):
            init_kwargs[field.name] = value = data.get(field.name)
            field_type: type = fieldtypes[field.name]

            # optional dataclass case
            if isinstance(field_type, UnionType):
                field_type = next(
                    (arg for arg in get_args(field_type) if arg is not type(None)),
                    None,
                )

                if field_type is None:
                    continue

            # straight forward
            if (
                isinstance(value, dict)
                and is_dataclass(field_type)
                and issubclass(field_type, BaseData)
            ):
                init_kwargs[field.name] = field_type.from_dict(value)
            # list of dataclasses
            elif (
                isinstance(value, list)
                and is_dataclass(field_type := get_args(field_type)[0])
                and issubclass(field_type, BaseData)
            ):
                init_kwargs[field.name] = [
                    field_type.from_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]

        return cls(**init_kwargs)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MessageData(BaseData):
    type: str
    data: dict | None = None


@dataclass
class PlayerInfoData(BaseData):
    id: str
    name: str
    tiles: list[TileData] | None = None

    @classmethod
    def from_player(cls, player: Player, with_tiles: bool = False) -> PlayerInfoData:
        obj = cls(player.id, player.name)

        if with_tiles:
            obj.tiles = [TileData.from_tile(tile) for tile in player.tiles]

        return obj

    def to_player(self) -> Player:
        player = Player(self.name, self.id)

        if self.tiles is not None:
            player.tiles = [tile.to_tile() for tile in self.tiles]

        return player


@dataclass
class TileData(BaseData):
    id: str
    symbol: str
    points: int

    @classmethod
    def from_tile(cls, tile: Tile) -> TileData:
        return cls(
            id=tile.id,
            symbol=tile.symbol,
            points=tile.points,
        )

    def to_tile(self) -> Tile:
        return Tile(self.symbol, self.points, self.id)


@dataclass
class FieldData(BaseData):
    row: int
    column: int
    type: int
    tile: TileData | None = None

    @classmethod
    def from_field(cls, field: Field) -> FieldData:
        obj = cls(
            row=field.row,
            column=field.column,
            type=field.type.value,
        )

        if field.tile:
            obj.tile = TileData.from_tile(field.tile)

        return obj


@dataclass
class BoardData(BaseData):
    fields: list[FieldData]
    rows: int
    columns: int

    @classmethod
    def from_board(cls, board: Board) -> BoardData:
        return cls(
            fields=[FieldData.from_field(field) for field in board.all_fields],
            rows=board.rows,
            columns=board.columns,
        )


class ClientData:
    @dataclass
    class CreateRoomData(BaseData):
        room_number: int
        player_name: str

    @dataclass
    class JoinRoomData(BaseData):
        room_number: int
        player_name: str

    @dataclass
    class PlaceTilesData(BaseData):
        tile_ids: list[str]
        field_positions: list[tuple[int, int]]


# server data


class ServerData:
    @dataclass
    class NewRoomData(BaseData):
        room_number: int
        player_info: PlayerInfoData

    @dataclass
    class JoinRoomData(BaseData):
        room_number: int
        player_infos: list[PlayerInfoData]

    @dataclass
    class NewPlayerData(BaseData):
        player_info: PlayerInfoData

    @dataclass
    class NewGameData(BaseData):
        player_info: PlayerInfoData
        player_infos: list[PlayerInfoData]
        board: BoardData

    @dataclass
    class NewTilesData(BaseData):
        tiles: list[dict]
