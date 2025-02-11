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
    Input,
    Select,
    MaskedInput,
)
# from textual import log
from textual.validation import Validator, ValidationResult

from routine import (
    DurationExercise,
    Exercise,
    RepetitionExercise,
    Routine,
    load_routines,
)
from utils import repetitions_to_str, seconds_to_time_str


class TimeValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        cleaned = value.replace(":", "")

        if not cleaned:
            return self.success()

        if len(cleaned) >= 4:
            minutes = int(cleaned[2:4])
            if minutes > 59:
                return self.failure("Minutes must be 00-59")

        if len(cleaned) >= 6:
            seconds = int(cleaned[4:6])
            if seconds > 59:
                return self.failure("Seconds must be 00-59")

        return self.success()


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


class TimeMaskedInput(MaskedInput):
    def __init__(self, *args, **kwargs):
        kwargs.update(
            {
                "template": "99:99:99;0",
                "placeholder": "HH:MM:SS",
                "validators": [TimeValidator()],
            }
        )
        super().__init__(*args, **kwargs)


class ExerciseInputWidget(HorizontalGroup):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Exercise Name")
        options = [("Duration Exercise", 1), ("Repetition Exercise", 2)]
        e_type: Select[int] = Select(options, allow_blank=False, value=1)
        e_type.border_title = "Exercise Type"
        yield e_type
        self.duration_input = TimeMaskedInput(classes="hide")
        self.duration_input.border_title = "Exercise Duration"
        yield self.duration_input
        self.rep_input = Input(
            placeholder="No. of repetitions", type="integer", classes="hide"
        )
        yield self.rep_input
        yield HorizontalGroup(
            Button("Add", id="add-btn"), Button("Cancel", id="cancel-btn")
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "add-btn":
            self.add_class("hide")
            # TODO: actually add the exercise
        if button_id == "cancel-btn":
            self.add_class("hide")

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.value == 1:
            self.duration_input.remove_class("hide")
            self.rep_input.add_class("hide")
        elif event.value == 2:
            self.rep_input.remove_class("hide")
            self.duration_input.add_class("hide")


class RoutineWidget(HorizontalGroup):
    """A routine widget."""

    BINDINGS = [
        ("a", "add_exercise", "Add Exercise"),
        ("r", "remove_exercise", "Remove Exercise"),
    ]

    def __init__(
        self, r_name: str, exercises: list[Exercise], *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.r_name = r_name.replace(" ", "-")
        self.exercises = exercises

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(
            Label(
                self.r_name,
                id=f"{self.r_name}-routine",
                classes="routine-name",
            ),
            HorizontalGroup(
                Button("Start", id="start-btn"),
                Button("Edit", id="edit-btn"),
                classes="routine-actions",
            ),
            classes="routine-header",
        )
        self.e_input = ExerciseInputWidget(id="exercise-input", classes="hide")
        yield self.e_input
        yield VerticalScroll(
            *[self._create_exercise_widget(e) for e in self.exercises],
            id=f"{self.r_name}-exercises",
            classes="exercises-scroll",
        )

    def _create_exercise_widget(self, e: Exercise) -> ExerciseWidget:
        if isinstance(e, DurationExercise):
            return DurationExerciseWidget(e.name, e.duration)
        elif isinstance(e, RepetitionExercise):
            return RepetitionExerciseWidget(e.name, e.repetitions)

    def action_add_exercise(self) -> None:
        self.e_input.remove_class("hide")

    def action_remove_exercise():
        pass


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
        self.app.switch_screen(RoutinesSelectScreen())


class RoutinesSelectScreen(Screen):
    """Screen with all routines"""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        items = (
            ListItem(Label(r.name), name=str(idx))
            for idx, r in enumerate(self.app.routines)
        )
        lv = ListView(*items, classes="routines-list")
        lv.border_title = "Select Routine: "
        yield lv

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Event handler called when list item is selected."""
        idx = int(event.item.name)
        self.app.switch_screen(RoutineScreen(r_idx=idx))


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
        self.app.switch_screen(RoutinesSelectScreen())


class TimeroApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "timero.tcss"
    BINDINGS = [("h", "go_home", "Go to homepage")]

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

    def action_go_home(self) -> None:
        self.app.switch_screen("start")


if __name__ == "__main__":
    app = TimeroApp()
    app.run()
