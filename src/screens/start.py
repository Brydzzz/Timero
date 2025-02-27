from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button
from textual.containers import HorizontalGroup
from routine import load_routines


class StartScreen(Screen):
    """Start screen for the app"""

    BINDINGS = [
        ("l", "load_routine", "Load routines"),
        ("c", "create_routine", "Create new routine"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield HorizontalGroup(
            Button("Load Routine", id="load-btn"),
            Button("Create Routine", id="create-btn"),
            id="start-btns",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        if button_id == "load-btn":
            self.action_load_routine()
        elif button_id == "create-btn":
            pass

    def action_load_routine(self) -> None:
        self.app.routines = load_routines(self.app.path)
        self.log(f"Routines {self.app.routines}")
        self.app.screen_manager.go_to_routine_select()
