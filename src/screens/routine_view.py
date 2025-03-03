from textual.screen import Screen
from textual.widgets import Header, Footer

from widgets.routine_widget import RoutineWidget


class RoutineViewScreen(Screen):
    """Screen with selected routine"""

    BINDINGS = [("b", "go_back", "Back")]

    def compose(self):
        yield Header()
        yield Footer()
        yield RoutineWidget(id="routine-widget")

    def action_go_back(self) -> None:
        self.app.screen_manager.go_to_routine_select()
