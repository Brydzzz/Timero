from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup
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

from textual import log
from textual.validation import Validator, ValidationResult

from routine import (
    DurationExercise,
    Exercise,
    RepetitionExercise,
    Routine,
    load_routines,
    save_routines,
)
from utils import (
    duration_input_to_seconds,
    repetitions_to_str,
    seconds_to_time_str,
)


class IsEmptyValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        return (
            self.success() if len(value) != 0 else self.failure("Empty Input")
        )


class TimeValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        cleaned = value.replace(":", "")

        if len(cleaned) < 6:
            return self.failure("Input too short")

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
                "validators": [TimeValidator(), IsEmptyValidator()],
            }
        )
        super().__init__(*args, **kwargs)


DURATION_OPTION = 1
REPETITION_OPTION = 2


def create_exercise_widget(e: Exercise) -> ExerciseWidget:
    if isinstance(e, DurationExercise):
        return DurationExerciseWidget(e.name, e.duration)
    elif isinstance(e, RepetitionExercise):
        return RepetitionExerciseWidget(e.name, e.repetitions)


class ExerciseInputWidget(HorizontalGroup):

    def _is_form_valid(self) -> bool:
        if self.e_type.value == DURATION_OPTION:
            return all([self.e_name.is_valid, self.duration_input.is_valid])
        else:  # REPETITION_OPTION
            return all([self.e_name.is_valid, self.rep_input.is_valid])

    def compose(self) -> ComposeResult:
        self.e_name = Input(
            placeholder="Exercise Name",
            type="text",
            validators=[IsEmptyValidator()],
        )
        yield self.e_name
        options = [
            ("Duration Exercise", DURATION_OPTION),
            ("Repetition Exercise", REPETITION_OPTION),
        ]
        self.e_type: Select[int] = Select(options, allow_blank=False, value=1)
        self.e_type.border_title = "Exercise Type"
        yield self.e_type
        self.duration_input = TimeMaskedInput(classes="hide")
        self.duration_input.border_title = "Exercise Duration"
        yield self.duration_input
        self.rep_input = Input(
            placeholder="No. of repetitions",
            type="integer",
            classes="hide",
            validators=[IsEmptyValidator()],
        )
        yield self.rep_input
        yield HorizontalGroup(
            Button("Add", id="add-btn"), Button("Cancel", id="cancel-btn")
        )  # TODO: add edit button when updating exercise info

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "add-btn":
            if not self._is_form_valid():
                log("Form not valid")
                # TODO: show a popup for user
                return

            if self.e_type.value == DURATION_OPTION:
                new_exercise = DurationExercise(
                    self.e_name.value,
                    duration_input_to_seconds(self.duration_input.value),
                )
            elif self.e_type.value == REPETITION_OPTION:
                new_exercise = RepetitionExercise(
                    self.e_name.value, int(self.rep_input.value)
                )

            parent = self.screen.query_one("#routine-widget", RoutineWidget)

            new_widget = ListItem(create_exercise_widget(new_exercise))
            parent.query_one("#exercises-scroll").mount(new_widget)
            new_widget.scroll_visible()

            routine: Routine = self.app.routines[parent.r_idx]
            routine.add_exercise(new_exercise)

            save_routines(self.app.path, self.app.routines)
            self.add_class("hide")
        if button_id == "cancel-btn":
            self.add_class("hide")

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.value == DURATION_OPTION:
            self.duration_input.remove_class("hide")
            self.rep_input.add_class("hide")
        elif event.value == REPETITION_OPTION:
            self.rep_input.remove_class("hide")
            self.duration_input.add_class("hide")


class RoutineWidget(HorizontalGroup):
    """A routine widget."""

    BINDINGS = [
        ("a", "add_exercise", "Add Exercise"),
        ("r", "remove_exercise", "Remove Exercise"),
        ("e", "edit_exercise", "Edit Exercise"),
    ]

    def __init__(
        self,
        r_idx: int,
        r_name: str,
        exercises: list[Exercise],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.r_idx = r_idx
        self.r_name = r_name.replace(" ", "-")
        self.exercises = exercises

    def _show_exercise_form(
        self,
        name: str = "",
        duration: str = "",
        rep: str = "",
        type: int = DURATION_OPTION,
    ) -> None:
        self.e_input.e_name.value = name
        self.e_input.duration_input.value = duration
        self.e_input.rep_input.value = rep
        self.e_input.e_type.value = type
        self.e_input.remove_class("hide")
        self.e_input.e_name.focus()

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(
            Label(
                self.r_name,
                id=f"{self.r_name}-routine",
                classes="routine-name",
            ),
            HorizontalGroup(
                Button("Start", id="start-btn"),
                Button("Reorder", id="reorder-btn"),
                classes="routine-actions",
            ),
            classes="routine-header",
        )
        self.e_input = ExerciseInputWidget(id="exercise-input", classes="hide")
        yield self.e_input
        self.e_list = ListView(
            *[ListItem(create_exercise_widget(e)) for e in self.exercises],
            id="exercises-scroll",
        )
        yield self.e_list

    def action_add_exercise(self) -> None:
        self._show_exercise_form()

    def action_remove_exercise(self) -> None:
        selected_item = self.e_list.highlighted_child

        if selected_item is None or not self.e_list.has_focus:
            # TODO: popup for user
            return

        self.e_list.remove_children([selected_item])

        routine: Routine = self.app.routines[self.r_idx]
        routine.exercises.pop(self.e_list.index)

        save_routines(self.app.path, self.app.routines)

    def action_edit_exercise(self) -> None:
        selected_item = self.e_list.highlighted_child

        if selected_item is None or not self.e_list.has_focus:
            # TODO: popup for user
            return

        routine: Routine = self.app.routines[self.r_idx]
        e = routine.exercises[self.e_list.index]
        if isinstance(e, DurationExercise):
            self._show_exercise_form(
                name=e.name,
                duration=e.duration_mask_string(),
                type=DURATION_OPTION,
            )
        elif isinstance(e, RepetitionExercise):
            self._show_exercise_form(
                name=e.name, rep=str(e.repetitions), type=REPETITION_OPTION
            )


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
                r_idx=self.routine_idx,
                r_name=self.routine.name,
                exercises=self.routine.exercises,
                id="routine-widget",
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
