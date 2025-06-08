from dataclasses import dataclass
from typing import override

from textual.app import ComposeResult
from textual.containers import Container, VerticalGroup
from textual.message import Message
from textual.reactive import reactive, var
from textual.screen import Screen
from textual.widgets import Button, Header

from core.game.types import Position
from ui.models import BoardModel, PlayerModel
from ui.screens.dialog_screen import DialogScreen
from ui.widgets.board import Board
from ui.widgets.field import Field
from ui.widgets.move_buttons import MoveButtons
from ui.widgets.score_board import ScoreBoard
from ui.widgets.tile import Tile
from ui.widgets.tile_rack import TileRack


class GameScreen(Screen):
    @dataclass
    class SubmitTiles(Message):
        tile_positions: list[tuple[str, Position]]

    @dataclass
    class ExchangeTiles(Message):
        tile_ids: list[str]

    @dataclass
    class SkipTurn(Message):
        pass

    player: var[PlayerModel] = var(PlayerModel.empty)
    players: reactive[list[PlayerModel]] = reactive(list)
    current_player_id: var[str] = var(str)

    @property
    def is_my_turn(self) -> bool:
        return self.player.id == self.current_player_id

    @override
    def compose(self) -> ComposeResult:
        yield Header(name='Scrabble')

        with Container():
            yield Board()
            with VerticalGroup():
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
        self.placed_tiles = []

    def update_current_player(self, player_id: str) -> None:
        self.current_player_id = player_id
        self.query_one(MoveButtons).disabled = not self.is_my_turn
        self.query_one(ScoreBoard).update_current_player(self.current_player_id)

    def place_tile(self, tile: Tile, field: Field) -> None:
        if field.tile:
            self.remove_tile(field)

        tile.enabled = False
        field.tile = tile
        self.placed_tiles.append(field)

    def remove_tile(self, field: Field) -> None:
        assert field.tile, f'Given field {field!r} does not have tile.'

        field.tile.enabled = True
        self.placed_tiles.remove(field)
        field.tile = None

    def on_board_field_selected(self, message: Board.FieldSelected) -> None:
        tiles = self.query_one(TileRack).get_selected()
        tile = next(tiles, None)

        if tile is not None:
            self.place_tile(tile, message.field)
        elif message.field.tile is not None:
            self.remove_tile(message.field)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case 'submit':
                assert all(field.tile for field in self.placed_tiles)

                tile_positions = [
                    (field.tile.tile_model.id, field.position)
                    for field in self.placed_tiles
                ]

                self.post_message(self.SubmitTiles(tile_positions))
            case 'exchange':
                if not (tiles := tuple(self.query_one(TileRack).get_selected())):
                    self.notify(
                        message='You have to select at least one tile.',
                        title='Exchange Error',
                        severity='error',
                    )
                    return

                tiles_text = ' '.join(tile.text for tile in tiles)
                question = f'Are you sure you want to exchange these {len(tiles)} tiles?\n {tiles_text}'

                response = await self.app.push_screen_wait(
                    DialogScreen.yes_no(question)
                )
                if not response:
                    return

                tile_ids = [tile.tile_model.id for tile in tiles]
                self.post_message(self.ExchangeTiles(tile_ids))
            case 'skip':
                question = 'Are you sure you want to skip your turn?'

                response = await self.app.push_screen_wait(
                    DialogScreen.yes_no(question)
                )

                if not response:
                    return

                self.post_message(self.SkipTurn())
            case _:
                raise Exception(f'Unsupported button id {event.button.id!r}')
