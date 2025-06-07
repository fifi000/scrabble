from textual import events
from textual.css.scalar import Scalar, ScalarOffset, Unit
from textual.geometry import Offset
from textual.message import Message
from textual.reactive import reactive
from textual.visual import VisualType
from textual.widgets import Static


class Draggable(Static):
    class DragEnded(Message):
        pass

    mouse_at_drag_start: reactive[Offset | None] = reactive(None)
    offset_at_drag_start: reactive[Offset | None] = reactive(None)

    def __init__(
        self,
        content: VisualType = '',
        *,
        allow_horizontal_drag: bool = True,
        allow_vertical_drag: bool = True,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            content=content,
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

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

        assert self.mouse_at_drag_start is not None, (
            'Mouse position at drag start is not set.'
        )
        assert self.offset_at_drag_start is not None, 'Offset at drag start is not set.'

        x, y = self.styles.offset

        if self.allow_horizontal_drag:
            diff = event.screen_x - self.mouse_at_drag_start.x
            x = self.offset_at_drag_start.x + diff
            x = Scalar(x, Unit.CELLS, Unit.WIDTH)

        if self.allow_vertical_drag:
            diff = event.screen_y - self.mouse_at_drag_start.y
            y = self.offset_at_drag_start.y + diff
            y = Scalar(y, Unit.CELLS, Unit.WIDTH)

        self.styles.offset = ScalarOffset(x, y)

    def on_mouse_up(self, event: events.MouseUp) -> None:
        if self.is_dragging:
            self.mouse_at_drag_start = None
            self.offset_at_drag_start = None
            self.release_mouse()
            event.stop()
            self.post_message(self.DragEnded())
