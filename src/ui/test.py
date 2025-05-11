from textual import events
from textual.app import App, ComposeResult
from textual.geometry import Offset
from textual.reactive import reactive
from textual.widgets import Static


class Draggable(Static):
    DEFAULT_CSS = """
    Draggable {
        width: auto;
    }
    """

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


class ExampleApp(App):
    CSS = """
    Screen {
        align: center middle
    }
    """

    def compose(self) -> ComposeResult:
        yield Draggable('Grab & move\n   __QQ\n  (_)_">\n  _)\n the mouse')


if __name__ == '__main__':
    app = ExampleApp()
    app.run()
