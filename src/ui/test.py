from rich.segment import Segment

from textual import events
from textual.app import App, ComposeResult
from textual.geometry import Offset
from textual.reactive import reactive
from textual.widgets import Static
from textual.app import App, ComposeResult
from textual.strip import Strip
from textual.widget import Widget


class Draggable(Static):
    mouse_at_drag_start: reactive[Offset | None] = reactive(None)
    offset_at_drag_start: reactive[Offset | None] = reactive(None)

    def on_mouse_down(self, event: events.MouseDown) -> None:
        self.mouse_at_drag_start = event.screen_offset
        self.offset_at_drag_start = Offset(
            round(self.styles.offset.x.value),
            round(self.styles.offset.y.value),
        )
        self.capture_mouse()

    def on_mouse_move(self, event: events.MouseMove) -> None:
        if (
            self.mouse_at_drag_start is not None
            and self.offset_at_drag_start is not None
        ):
            x = self.offset_at_drag_start.x + (
                event.screen_x - self.mouse_at_drag_start.x
            )
            y = self.offset_at_drag_start.y + (
                event.screen_y - self.mouse_at_drag_start.y
            )
            self.styles.offset = (x, y)

    def on_mouse_up(self, event: events.MouseUp) -> None:
        self.mouse_at_drag_start = None
        self.offset_at_drag_start = None
        self.release_mouse()
        event.stop()


class CheckerBoard(Widget):
    """Render an 8x8 checkerboard."""

    COMPONENT_CLASSES = {
        'checkerboard--white-square',
        'checkerboard--black-square',
    }

    DEFAULT_CSS = """
    CheckerBoard .checkerboard--white-square {
        background: #A5BAC9;
    }
    CheckerBoard .checkerboard--black-square {
        background: #004578;
    }
    """

    ROWS, COLS = 15, 15

    def render_line(self, y: int) -> Strip:
        """Render a line of the widget. y is relative to the top of the widget."""

        row_index = y // 2

        if row_index >= CheckerBoard.COLS:
            return Strip.blank(self.size.width)

        is_odd = row_index % 2

        white = self.get_component_rich_style('checkerboard--white-square')
        black = self.get_component_rich_style('checkerboard--black-square')

        segments = [
            Segment(
                str(1).center(5, ' '),
                black if (column + is_odd) % 2 else white,
            )
            for column in range(CheckerBoard.COLS)
        ]
        strip = Strip(segments, CheckerBoard.ROWS * CheckerBoard.COLS)
        return strip


class BoardApp(App):
    """A simple app to show our widget."""

    def compose(self) -> ComposeResult:
        yield CheckerBoard()


class DragDropApp(App):
    def compose(self) -> ComposeResult:
        yield Draggable('Drag me around!')


if __name__ == '__main__':
    BoardApp().run()
