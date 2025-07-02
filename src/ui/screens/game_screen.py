from __future__ import annotations

from dataclasses import dataclass
from typing import override

from textual import on
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.message import Message
from textual.reactive import reactive, var
from textual.screen import Screen
from textual.widgets import Button, Header

from ui.models.board_model import BoardModel
from ui.models.player_model import PlayerModel
from ui.screens.dialog_screen import DialogScreen
from ui.models.tile_model import TileModel
from ui.widgets.board import Board
from ui.widgets.field import Field
from ui.widgets.move_buttons import MoveButtons
from ui.widgets.score_board import ScoreBoard
from ui.widgets.tile import Tile
from ui.widgets.tile_rack import TileRack


class GameScreen(Screen):
    @dataclass
    class SubmitTiles(Message):
        tile_models: list[TileModel]

    @dataclass
    class ExchangeTiles(Message):
        tile_models: list[TileModel]

    @dataclass
    class SkipTurn(Message):
        pass

    player: var[PlayerModel] = var(PlayerModel.empty)
    players: reactive[list[PlayerModel]] = reactive(list)
    current_player_id: var[str] = var(str)
    occupied_fields: var[list[Field]] = var(list)

    @property
    def is_my_turn(self) -> bool:
        return self.player.id == self.current_player_id

    @override
    def compose(self) -> ComposeResult:
        yield Header(name='Scrabble')

        with VerticalScroll():
            yield Board()

            with VerticalScroll(id='right-panel'):
                yield TileRack()
                yield MoveButtons()
                yield ScoreBoard()

    def update_player(self, player_model: PlayerModel) -> None:
        self.player = player_model
        self.query_one(TileRack).update_tiles(self.player.tiles)

    def update_players(self, player_models: list[PlayerModel]) -> None:
        self.players = player_models
        self.query_one(ScoreBoard).update_players(self.players)

    def update_board(self, board_model: BoardModel) -> None:
        self.query_one(Board).update(board_model)
        self.occupied_fields = []

    def update_current_player(self, player_id: str) -> None:
        self.current_player_id = player_id
        self.query_one(MoveButtons).disabled = not self.is_my_turn
        self.query_one(ScoreBoard).update_current_player(self.current_player_id)

    def place_tile(self, tile: Tile, field: Field) -> None:
        if field.tile:
            self.remove_tile(field)

        tile.enabled = False
        field.tile = tile
        self.occupied_fields.append(field)

    def remove_tile(self, field: Field) -> None:
        assert field.tile, f'Given field {field!r} does not have tile.'

        field.tile.enabled = True
        self.occupied_fields.remove(field)
        field.tile = None

    def on_board_field_selected(self, message: Board.FieldSelected) -> None:
        tiles = self.query_one(TileRack).get_selected()
        tile = next(tiles, None)

        if tile is not None:
            self.place_tile(tile, message.field)
        elif message.field.tile is not None:
            self.remove_tile(message.field)

    @on(Button.Pressed, '#submit')
    async def handle_submit(self) -> None:
        assert all(field.tile for field in self.occupied_fields)

        tile_models: list[TileModel] = []

        for field in self.occupied_fields:
            assert field.tile

            field.tile.model.position = field.position
            tile_models.append(field.tile.model)

        tile_models.sort(key=lambda x: x.position)  # type: ignore # i asing this above so i am pretty sure it's not None

        blanks = [model for model in tile_models if model.points == 0]

        for i, blank in enumerate(blanks, start=1):
            value = await self.app.push_screen_wait(
                DialogScreen.prompt(
                    f'Choose letter for blank #{i}',
                    input_init_kwargs={'max_length': 1, 'valid_empty': False},
                )
            )
            # TODO: in the future lowercase letter may be valid, when room configuration will be added
            #       so this would be better to check if the `value` is valid then `value.upper()`
            blank.symbol = value.upper()

        self.post_message(self.SubmitTiles(tile_models))

    @on(Button.Pressed, '#exchange')
    async def handle_exchange(self) -> None:
        if not (tiles := tuple(self.query_one(TileRack).get_selected())):
            self.notify(
                message='You have to select at least one tile.',
                title='Exchange Error',
                severity='error',
            )
            return

        tiles_text = ' '.join(tile.text for tile in tiles)
        question = (
            f'Are you sure you want to exchange these {len(tiles)} tiles?\n{tiles_text}'
        )

        response = await self.app.push_screen_wait(DialogScreen.yes_no(question))
        if response:
            models = [tile.model for tile in tiles]
            self.post_message(self.ExchangeTiles(models))

    @on(Button.Pressed, '#skip')
    async def handle_skip(self) -> None:
        question = 'Are you sure you want to skip your turn?'

        response = await self.app.push_screen_wait(DialogScreen.yes_no(question))
        if response:
            self.post_message(self.SkipTurn())
