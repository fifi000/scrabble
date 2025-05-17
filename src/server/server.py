import asyncio
import json
import uuid
from uuid import UUID

from websockets.asyncio.server import ServerConnection, serve

from core.enums.language import Language
from core.game import Game
from core.player import Player
from server.messages import (
    ClientMessageType,
    JoinGameData,
    Message,
    NewPlayerData,
    NewTiles,
    PlaceTilesData,
    ServerMessageType,
)

GAME: Game | None = None
PLAYERS: list[tuple[ServerConnection, Player]] = []


# player actions


async def handle_join_game(websocket: ServerConnection, data: JoinGameData) -> None:
    player_name = data.player_name
    player_id = uuid.uuid4()

    PLAYERS.append((websocket, Player(player_id, player_name)))

    await broadcast_to_game(
        Message(
            ServerMessageType.NEW_PLAYER,
            NewPlayerData(player_name, str(player_id)).to_dict(),
        )
    )


async def handle_start_game():
    global GAME

    GAME = Game(Language.POLISH)
    for ws, player in PLAYERS:
        GAME.add_player(player)

    GAME.start()

    for websocket, player in PLAYERS:
        await websocket.send(
            Message(
                ServerMessageType.GAME_STARTED,
                NewTiles(
                    [
                        {
                            'tile_id': str(tile.id),
                            'symbol': tile.symbol,
                            'points': tile.points,
                        }
                        for tile in player.tiles
                    ]
                ).to_dict(),
            ).to_json()
        )


async def handle_place_letters(websocket: ServerConnection, data: PlaceTilesData):
    assert GAME

    player = next((player for ws, player in PLAYERS if ws == websocket))

    new_tiles = GAME.place_tiles(
        player, list(map(UUID, data.tile_ids)), data.field_positions
    )

    await broadcast_to_game(Message(ServerMessageType.TILES_PLACED, data.to_dict()))

    await websocket.send(
        Message(
            ServerMessageType.NEW_TILES,
            NewTiles(
                [
                    {
                        'tile_id': str(tile.id),
                        'symbol': tile.symbol,
                        'points': tile.points,
                    }
                    for tile in new_tiles
                ]
            ).to_dict(),
        ).to_json()
    )


# server broadcasting


async def broadcast_to_game(message: Message) -> None:
    for websocket, player in PLAYERS:
        await websocket.send(message.to_json())


# client entry point


async def game_server(websocket: ServerConnection) -> None:
    async for ws_message in websocket:
        message = Message.from_dict(json.loads(ws_message))

        match message.type:
            case ClientMessageType.JOIN_GAME:
                assert message.data
                data = JoinGameData.from_dict(message.data)
                await handle_join_game(websocket, data)

            case ClientMessageType.START_GAME:
                await handle_start_game()

            case ClientMessageType.PLACE_TILES:
                assert message.data
                data = PlaceTilesData.from_dict(message.data)
                await handle_place_letters(websocket, data)

            case _:
                raise Exception(f'Unsupported value: {message.type!r}')


async def main():
    async with serve(game_server, 'localhost', 8765) as server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
