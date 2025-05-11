from core.enums.field_type import FieldType
from core.field import Field as GameField

from textual.widgets import Static
from textual.reactive import reactive


class Field(Static):
    text = reactive('')

    def __init__(self, game_field: GameField, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.game_field = game_field

    def render(self) -> str:
        return self.text

    @property
    def bg_color(self) -> str | None:
        # a tile is placed
        if not self.game_field.is_empty:
            return 'yellow'

        match self.game_field.type:
            case FieldType.STANDARD:
                return None
            case FieldType.DOUBLE_LETTER:
                return '#57a9c2'
            case FieldType.TRIPPLE_LETTER:
                return '#5774c2'
            case FieldType.DOUBLE_WORD:
                return '#9c733e'
            case FieldType.TRIPPLE_WORD:
                return '#ce1717'

    def on_mount(self) -> None:
        self.styles.background = self.bg_color
