from widgets.routine_widget import RoutineWidget
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer


class CreateRoutineView(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield RoutineWidget(create_mode=True)
        yield Footer()
