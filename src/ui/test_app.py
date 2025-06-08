from __future__ import annotations

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.content import ContentText
from textual.screen import ModalScreen, Screen
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
        if full_screen:
            DialogScreen.DEFAULT_CSS = DialogScreen.DEFAULT_CSS.replace(
                'max-width: 60;', ''
            )

        super().__init__(name=name, id=id, classes=classes)

    def compose(self) -> ComposeResult:
        yield Container(*self.widgets, id='container')

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
    def prompt(question: VisualType) -> DialogScreen[str]:
        prompt = _Prompt(question=question)

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
    }
    """

    def __init__(
        self,
        question: VisualType,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self.question = question
        super().__init__(name=name, id=id, classes=classes)

    def compose(self) -> ComposeResult:
        yield Label(self.question, id='question')
        with Horizontal(id='buttons'):
            yield Input()

    @on(Input.Submitted)
    def handle_submit(self) -> None:
        value = self.query_one(Input).value
        self.screen.dismiss(value)


class _Message(Static):
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

    def compose(self) -> ComposeResult:
        yield Label(self.title)
        yield Label(self.text)


class BasicScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Button('Yes / No', variant='primary', id='yes-no')
        yield Button('Prompt', variant='primary', id='prompt')
        yield Button('Message', variant='primary', id='message')
        yield Button('Dummy', variant='primary', id='dummy')

    @on(Button.Pressed, '#yes-no')
    def handle_yes_no(self) -> None:
        self.app.push_screen(DialogScreen.yes_no('Dummy question?'))

    @on(Button.Pressed, '#prompt')
    def handle_prompt(self) -> None:
        self.app.push_screen(
            DialogScreen.prompt("This is not an eye test\nIt's a gay test")
        )

    @on(Button.Pressed, '#message')
    def handle_message(self) -> None:
        self.app.push_screen(DialogScreen.message('karma wraca'))

    @on(Button.Pressed, '#dummy')
    def handle_dummy(self) -> None:
        self.app.push_screen(DialogScreen(Label('Dupa')))


class TestApp(App):
    CSS = """
        BasicScreen {
            background: pink;
            align: center middle;
        }

        Button {
            width: auto;
        }
    """

    def on_mount(self) -> None:
        self.push_screen(BasicScreen())


if __name__ == '__main__':
    TestApp().run()
