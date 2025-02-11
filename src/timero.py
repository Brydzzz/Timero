from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import (
    HorizontalGroup,
    VerticalScroll,
)
from textual.screen import Screen
from textual.reactive import reactive, var
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    Static,
    ListView,
    ListItem,
)

from routine import (
    DurationExercise,
    Exercise,
    RepetitionExercise,
    Routine,
    load_routines,
)
from utils import repetitions_to_str, seconds_to_time_str


class ExerciseWidget(HorizontalGroup):
    """An exercise widget"""

    def __init__(self, e_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.e_name = e_name

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(
            Label(self.e_name, classes="exercise-name"),
        )


class DurationExerciseWidget(ExerciseWidget):
    def __init__(self, e_name: str, duration: int, *args, **kwargs):
        super().__init__(e_name, *args, **kwargs)
        self.duration = duration

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(
            Label(self.e_name),
            Label(seconds_to_time_str(self.duration), classes="duration"),
        )


class RepetitionExerciseWidget(ExerciseWidget):
    def __init__(self, e_name: str, repetitions: int, *args, **kwargs):
        super().__init__(e_name, *args, **kwargs)
        self.repetitions = repetitions

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(
            Label(self.e_name),
            Label(repetitions_to_str(self.repetitions), classes="repetitions"),
        )


class RoutineWidget(HorizontalGroup):
    """A routine widget."""

    def __init__(
        self, r_name: str, exercises: list[Exercise], *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.r_name = r_name.replace(" ", "-")
        self.exercises = exercises

    def compose(self) -> ComposeResult:
        yield Label(
            self.r_name, id=f"{self.r_name}-routine", classes="routine-name"
        )
        yield VerticalScroll(
            id=f"{self.r_name}-exercises", classes="exercises-scroll"
        )

    def on_mount(self) -> None:
        exercise_container = self.query_one(f"#{self.r_name}-exercises")
        for e in self.exercises:
            if isinstance(e, DurationExercise):
                new_exercise = DurationExerciseWidget(e.name, e.duration)
            elif isinstance(e, RepetitionExercise):
                new_exercise = RepetitionExerciseWidget(e.name, e.repetitions)
            exercise_container.mount(new_exercise)


class RoutineScreen(Screen):
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
                r_name=self.routine.name, exercises=self.routine.exercises
            )
        )

    def action_go_back(self) -> None:
        self.app.switch_screen("select-routine")


class RoutinesSelectScreen(Screen):
    """Screen with all routines"""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Label("Select Routine")
        items = (
            ListItem(Label(r.name), name=str(idx))
            for idx, r in enumerate(self.app.routines)
        )
        yield ListView(*items)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Event handler called when list item is selected."""
        idx = int(event.item.name)
        self.app.push_screen(RoutineScreen(r_idx=idx))


class StartScreen(Screen):
    """Start screen for the app"""

    BINDINGS = [
        ("l", "load_routine", "Load routine"),
        ("c", "create_routine", "Create routine"),
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
        self.app.install_screen(RoutinesSelectScreen(), name="select-routine")
        self.app.switch_screen("select-routine")


class TimeroApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "timero.tcss"

    routines: list[Routine] = reactive(None)
    path = var(Path(__file__).parent.parent / "routines.json")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield Static("App")

    def on_mount(self) -> None:
        self.install_screen(StartScreen(id="start"), name="start")
        self.push_screen("start")
        self.theme = "dracula"


if __name__ == "__main__":
    app = TimeroApp()
    app.run()
