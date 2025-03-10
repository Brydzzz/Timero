from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button
from textual.containers import HorizontalGroup


class Homepage(Screen):
    """Homepage for the app"""

    BINDINGS = [
        ("l", "load_routine", "Load routines"),
        ("c", "create_routine", "Create new routine"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield HorizontalGroup(
            Button("Load Routines", id="load-btn"),
            Button("Create Routine", id="create-btn"),
            id="start-btns",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "load-btn":
            self.action_load_routine()
        elif button_id == "create-btn":
            self.action_create_routine()

    def action_load_routine(self) -> None:
        self.app.routines = self.app.routine_controller.load_routines()
        self.app.screen_manager.go_to_routine_select()

    def action_create_routine(self) -> None:
        self.app.switch_screen("create-routine")
