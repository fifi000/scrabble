from textual import events
from textual.geometry import Offset
from textual.reactive import reactive
from textual.widgets import Static
from textual.css.scalar import ScalarOffset, Scalar, Unit
from textual.message import Message


class Draggable(Static):
    class DragEnded(Message):
        def __init__(self) -> None:
            super().__init__()

    mouse_at_drag_start: reactive[Offset | None] = reactive(None)
    offset_at_drag_start: reactive[Offset | None] = reactive(None)

    def __init__(
        self,
        allow_horizontal_drag: bool = True,
        allow_vertical_drag: bool = True,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.allow_horizontal_drag = allow_horizontal_drag
        self.allow_vertical_drag = allow_vertical_drag

    @property
    def allow_drag(self) -> bool:
        return self.allow_horizontal_drag or self.allow_vertical_drag

    @property
    def is_dragging(self) -> bool:
        return (
            self.mouse_at_drag_start is not None
            and self.offset_at_drag_start is not None
        )

    def on_mouse_down(self, event: events.MouseDown) -> None:
        if not self.allow_drag:
            return

        # let's save current screen and parent offset
        self.mouse_at_drag_start = event.screen_offset
        self.offset_at_drag_start = Offset(
            round(self.styles.offset.x.value),
            round(self.styles.offset.y.value),
        )

        self.capture_mouse()

    def on_mouse_move(self, event: events.MouseMove) -> None:
        if not self.is_dragging:
            return

        x, y = self.styles.offset

        if self.allow_horizontal_drag:
            x = self.offset_at_drag_start.x + (
                event.screen_x - self.mouse_at_drag_start.x
            )
            x = Scalar(x, Unit.CELLS, Unit.WIDTH)

        if self.allow_vertical_drag:
            y = self.offset_at_drag_start.y + (
                event.screen_y - self.mouse_at_drag_start.y
            )
            y = Scalar(y, Unit.CELLS, Unit.WIDTH)

        self.styles.offset = ScalarOffset(x, y)

    def on_mouse_up(self, event: events.MouseUp) -> None:
        if self.is_dragging:
            self.mouse_at_drag_start = None
            self.offset_at_drag_start = None
            self.release_mouse()
            event.stop()
            self.post_message(self.DragEnded())
