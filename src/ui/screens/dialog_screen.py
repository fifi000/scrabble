from __future__ import annotations

from typing import Any, override

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.content import ContentText
from textual.screen import ModalScreen
from textual.visual import VisualType
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Static


class DialogScreen[ScreenResultType](ModalScreen[ScreenResultType]):
    DEFAULT_CSS = """
    DialogScreen {
        align: center middle;
        
        #container {
            background: $panel;
            margin: 4 8;
            padding: 1 2;
            height: auto;
            max-width: 60;
        }
    }
    """

    BINDINGS = [('escape', 'dismiss', 'Dismiss')]

    def __init__(
        self,
        *widgets: Widget,
        full_screen: bool = False,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self.widgets = widgets
        self.full_screen = full_screen

        super().__init__(name=name, id=id, classes=classes)

    @override
    def compose(self) -> ComposeResult:
        classes = 'full-screen' if self.full_screen else ''
        yield Container(*self.widgets, id='container', classes=classes)

    @staticmethod
    def yes_no(
        question: VisualType,
        *,
        yes_text: ContentText | None = None,
        no_text: ContentText | None = None,
    ) -> DialogScreen[bool]:
        yes_no = _YesNo(question=question, yes_text=yes_text, no_text=no_text)

        return DialogScreen[bool](yes_no)

    @staticmethod
    def prompt(
        question: VisualType, *, input_init_kwargs: dict[str, Any] | None = None
    ) -> DialogScreen[str]:
        prompt = _Prompt(question=question, input_init_kwargs=input_init_kwargs)

        return DialogScreen[str](prompt)

    @staticmethod
    def message(text: VisualType, title: VisualType = '') -> DialogScreen[None]:
        message = _Message(text=text, title=title)

        return DialogScreen[None](message)


class _YesNo(Static):
    DEFAULT_CSS = """
    _YesNo {
        #question {
            content-align: center middle;
            text-style: bold;
            width: 1fr;
        }   

        #buttons {                    
            align: center middle;
            margin-top: 1;
            width: 1fr;                
            height: auto;                    
        }

        Button {
            margin: 0 1;
        }
    }
    """

    def __init__(
        self,
        question: VisualType,
        *,
        yes_text: ContentText | None = None,
        no_text: ContentText | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self.question = question
        self.yes_text = yes_text or 'Yes'
        self.no_text = no_text or 'No'

        super().__init__(name=name, id=id, classes=classes)

    @override
    def compose(self) -> ComposeResult:
        yield Label(self.question, id='question')
        with Horizontal(id='buttons'):
            yield Button.success(self.yes_text, id='yes')
            yield Button.error(self.no_text, id='no')

    @on(Button.Pressed, '#yes')
    def handle_yes(self) -> None:
        self.screen.dismiss(True)

    @on(Button.Pressed, '#no')
    def handle_no(self) -> None:
        self.screen.dismiss(False)


class _Prompt(Static):
    DEFAULT_CSS = """
    _Prompt {        
        #question {
            content-align: center middle;
            text-style: bold;
            width: 1fr;
        }   

        #buttons {                    
            align: center middle;
            width: 1fr;                
            height: auto;                    
        }

        Input {
            margin-top: 1;
            width: 1fr;                
        }

        Button {
            margin-top: 1;
        }
    }
    """

    def __init__(
        self,
        question: VisualType,
        *,
        input_init_kwargs: dict[str, Any] | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self.question = question
        self.input_init_kwargs = input_init_kwargs or {}

        super().__init__(name=name, id=id, classes=classes)

    @override
    def compose(self) -> ComposeResult:
        yield Label(self.question, id='question')
        with Horizontal(id='buttons'):
            input_ = Input(**self.input_init_kwargs)
            input_.focus()
            yield input_
            yield Button('Submit', variant='primary', id='submit')

    @on(Input.Submitted)
    def handle_submit(self) -> None:
        value = self.query_one(Input).value
        self.screen.dismiss(value)

    @on(Button.Pressed, '#submit')
    def handle_button_submit(self) -> None:
        value = self.query_one(Input).value
        self.screen.dismiss(value)


class _Message(Static):
    DEFAULT_CSS = """
    _Message {
        #title {
            content-align: center middle;
            text-style: bold;
            margin-bottom: 1;
        }
        
        #text {
            content-align: center middle;
        }
    }
    """

    def __init__(
        self,
        text: VisualType,
        title: VisualType = '',
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        self.text = text
        self.title = title

        super().__init__(
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    @override
    def compose(self) -> ComposeResult:
        if self.title:
            yield Label(self.title, id='title')
        yield Label(self.text, id='text')
