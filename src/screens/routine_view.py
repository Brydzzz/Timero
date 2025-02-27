from textual.screen import Screen
from textual.widgets import Header, Footer
from timero import RoutineWidget


class RoutineViewScreen(Screen):
    """Screen with selected routine"""

    BINDINGS = [("b", "go_back", "Go back to select routine")]

    def __init__(self, r_idx: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.routine_idx = r_idx
        self.routine = self.app.routines[r_idx]

    def compose(self):
        yield Header()
        yield Footer()
        yield (
            RoutineWidget(
                r_idx=self.routine_idx,
                r_name=self.routine.name,
                exercises=self.routine.exercises,
                id="routine-widget",
            )
        )

    def action_go_back(self) -> None:
        self.app.screen_manager.go_to_routine_select()
