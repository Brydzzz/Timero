from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button
from textual.containers import HorizontalGroup

from screens.create_routine import CreateRoutineView


class Homepage(Screen):
    """Homepage for the app"""

    BINDINGS = [
        ("l", "go_to_routines", "List of routines"),
        ("c", "create_routine", "Create new routine"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield HorizontalGroup(
            Button("List Of Routines", id="list-btn"),
            Button("Create Routine", id="create-btn"),
            id="start-btns",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "list-btn":
            self.action_go_to_routines()
        elif button_id == "create-btn":
            self.action_create_routine()

    def action_go_to_routines(self) -> None:
        self.app.screen_manager.go_to_routine_select()

    def action_create_routine(self) -> None:
        self.app.switch_screen(CreateRoutineView())
