from textual.containers import VerticalGroup, Container
from textual.widgets import Label, Button
from art import text2art
from textual.app import ComposeResult


class TrainingEndWidget(VerticalGroup):
    DEFAULT_CSS = """
        TrainingEndWidget {
            background: $boost;
            align: center middle;
            max-width: 55vw;
            max-height: 65vh;
            height: auto;
            margin: 1;
            padding: 1;
            content-align: center middle;

            & > Label {
            text-align: center;
            width: 100%;
            }
        }

        #button-container {
            align-horizontal: center;
            align-vertical: bottom;
            width: 100%;
        }
    """

    def __init__(self, routine_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.routine_name = routine_name

    def compose(self) -> ComposeResult:
        yield Label(
            text2art("CONGRATS!!!", "straight"),
            id="congrats-label",
        )
        yield Label(f"You have finished {self.routine_name} :)")
        with Container(id="button-container"):
            yield Button("Exit", id="exit-training", variant="success")

    def on_mount(self) -> None:
        self.query_one("#exit-training", Button).focus()
