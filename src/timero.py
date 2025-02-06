from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.screen import Screen
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Label, Static

from routine import (
    DurationExercise,
    Exercise,
    RepetitionExercise,
    Routine,
    load_routines,
)


class ExerciseWidget(HorizontalGroup):
    """An exercise widget"""

    def __init__(self, e_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.e_name = e_name

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(
            Label(self.e_name, id="exercise-name"),
        )


class DurationExerciseWidget(ExerciseWidget):
    def __init__(self, e_name: str, duration: int, *args, **kwargs):
        super().__init__(e_name, *args, **kwargs)
        self.duration = duration

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(Label(self.e_name), Label(str(self.duration)))


class RepetitionExerciseWidget(ExerciseWidget):
    def __init__(self, e_name: str, repetitions: int, *args, **kwargs):
        super().__init__(e_name, *args, **kwargs)
        self.repetitions = repetitions

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(Label(self.e_name), Label(str(self.repetitions)))


class RoutineWidget(HorizontalGroup):
    """A routine widget."""

    def __init__(
        self, r_name: str, exercises: list[Exercise], *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.r_name = r_name.replace(" ", "-")
        self.exercises = exercises

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(
            Label(self.r_name, id="routine-name"), id=f"{self.r_name}-routine"
        )
        for e in self.exercises:
            if isinstance(e, DurationExercise):
                new_exercise = DurationExerciseWidget(e.name, e.duration)
            elif isinstance(e, RepetitionExercise):
                new_exercise = RepetitionExerciseWidget(e.name, e.repetitions)
            self.mount(new_exercise)


class RoutinesScreen(Screen):
    """Screen with all routines"""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield VerticalScroll(id="routines")

    def on_mount(self) -> None:
        routines_container = self.query_one("#routines")

        for routine in self.app.routines:
            new_routine = RoutineWidget(routine.name, routine.exercises)
            routines_container.mount(new_routine)
            new_routine.scroll_visible()


class StartScreen(Screen):
    """Start screen for the app"""

    BINDINGS = [
        ("l", "load_routine", "Load routine"),
        ("c", "create_routine", "Create routine"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
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
        self.app.routines = load_routines("routines.json")
        self.log(f"Routines {self.app.routines}")
        self.app.install_screen(RoutinesScreen(), name="routines")
        self.app.switch_screen("routines")


class TimeroApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "timero.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    routines: list[Routine] = reactive(None)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield Static("App")

    def on_mount(self) -> None:
        self.install_screen(StartScreen(id="start"), name="start")
        self.push_screen("start")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark"
            if self.theme == "textual-light"
            else "textual-light"
        )


if __name__ == "__main__":
    app = TimeroApp()
    app.run()
