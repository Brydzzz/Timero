from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
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
from screens.start import StartScreen
from routine import (
    DurationExercise,
    Exercise,
    RepetitionExercise,
    Routine,
    save_routines,
)

from screens.manager import ScreenManager
from utils import (
    duration_input_to_seconds,
    repetitions_to_str,
    seconds_to_time_str,
)
from widgets._timer import Timer


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

    def __init__(self, exercise, e_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs, classes="exercise-widget")
        self.e_name = e_name
        self.exercise = exercise

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(
            Label(self.e_name, classes="exercise-name"),
        )


class DurationExerciseWidget(ExerciseWidget):
    def __init__(self, exercise, e_name: str, duration: int, *args, **kwargs):
        super().__init__(exercise, e_name, *args, **kwargs)
        self.duration = duration

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(
            Label(self.e_name),
            Label(seconds_to_time_str(self.duration), classes="duration"),
        )


class RepetitionExerciseWidget(ExerciseWidget):
    def __init__(
        self, exercise, e_name: str, repetitions: int, *args, **kwargs
    ):
        super().__init__(exercise, e_name, *args, **kwargs)
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
        return DurationExerciseWidget(e, e.name, e.duration)
    elif isinstance(e, RepetitionExercise):
        return RepetitionExerciseWidget(e, e.name, e.repetitions)


class ExerciseInputWidget(HorizontalGroup):

    def _is_form_valid(self) -> bool:
        if self.e_type.value == DURATION_OPTION:
            return all([self.e_name.is_valid, self.duration_input.is_valid])
        else:  # REPETITION_OPTION
            return all([self.e_name.is_valid, self.rep_input.is_valid])

    def _create_exercise(self) -> None:
        if self.e_type.value == DURATION_OPTION:
            new_exercise = DurationExercise(
                self.e_name.value,
                duration_input_to_seconds(self.duration_input.value),
            )
        elif self.e_type.value == REPETITION_OPTION:
            new_exercise = RepetitionExercise(
                self.e_name.value, int(self.rep_input.value)
            )
        return new_exercise

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
            Button("Add", id="add-btn"),
            Button("Save", id="save-exercise-edit-btn"),
            Button("Cancel", id="cancel-btn"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "add-btn":
            if not self._is_form_valid():
                log("Form not valid")
                self.app.notify(
                    message="Inputs are not valid",
                    title="Cannot Save Exercise",
                    severity="error",
                )
                return

            new_exercise = self._create_exercise()

            new_widget = ListItem(create_exercise_widget(new_exercise))
            self.parent.query_one("#exercises-scroll").mount(new_widget)
            new_widget.scroll_visible()

            routine: Routine = self.app.routines[self.parent.r_idx]
            routine.add_exercise(new_exercise)

            save_routines(self.app.path, self.app.routines)
            self.add_class("hide")
        elif button_id == "save-exercise-edit-btn":
            if not self._is_form_valid():
                log("Form not valid")
                self.app.notify(
                    message="Inputs are not valid",
                    title="Cannot Save Exercise",
                    severity="error",
                )
                return

            e = self.parent.exercise_to_edit
            routine: Routine = self.app.routines[self.parent.r_idx]

            if (
                isinstance(e, DurationExercise)
                and self.e_type == DURATION_OPTION
            ):
                e.name = self.e_name.value
                e.duration = duration_input_to_seconds(
                    self.duration_input.value
                )
            elif (
                isinstance(e, RepetitionExercise)
                and self.e_type == REPETITION_OPTION
            ):
                e.name = self.e_name.value
                e.repetitions = int(self.rep_input.value)
            else:  # Exercise type changed
                new_exercise = self._create_exercise()
                routine.replace_exercise(
                    new_exercise, self.parent.exercise_to_edit_idx
                )
                e = new_exercise

            # Update widget
            self.parent.exercise_to_edit_widget.remove_children()
            new_exercise_widget = create_exercise_widget(e)
            self.parent.exercise_to_edit_widget.mount(new_exercise_widget)

            save_routines(self.app.path, self.app.routines)
            self.add_class("hide")
        elif button_id == "cancel-btn":
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

    exercise_to_edit: DurationExercise | RepetitionExercise = reactive(None)
    exercise_to_edit_idx: int = reactive(None)
    exercise_to_edit_widget: ExerciseWidget = reactive(None)

    class ReorderWidget(HorizontalGroup):

        def _get_exercise_to_move(self) -> tuple[int, Exercise]:
            e_list: ListView = self.parent.e_list
            index = e_list.index
            item: ListItem = e_list.highlighted_child
            e_widget: ExerciseWidget = item.query_one(".exercise-widget")
            exercise_moved = e_widget.exercise
            return index, exercise_moved

        def _move_exercise(self, index, target_index, exercise) -> None:
            e_list: ListView = self.parent.e_list
            e_list.pop(index)
            e_list.insert(
                target_index,
                [ListItem(create_exercise_widget(exercise))],
            )
            e_list.index = target_index

        def compose(self) -> ComposeResult:
            yield Button("🔼", id="move-up", classes="icon-btn")
            yield Button("⏫", id="move-top", classes="icon-btn")
            yield Button("🔽", id="move-down", classes="icon-btn")
            yield Button("⏬", id="move-bottom", classes="icon-btn")
            yield Button("Save", id="save-reorder")
            yield Button("Cancel", id="cancel-reorder", variant="error")

        def on_button_pressed(self, event: Button.Pressed) -> None:
            button_id = event.button.id
            match button_id:
                case "move-up":
                    index, e = self._get_exercise_to_move()

                    if index > 0:
                        self._move_exercise(index, index - 1, e)
                case "move-top":
                    index, e = self._get_exercise_to_move()

                    if index != 0:
                        self._move_exercise(index, 0, e)
                case "move-down":
                    index, e = self._get_exercise_to_move()
                    e_list: ListView = self.parent.e_list

                    if index < len(e_list.children) - 1:
                        self._move_exercise(index, index + 2, e)
                case "move-bottom":
                    index, e = self._get_exercise_to_move()
                    length = len(self.parent.e_list.children)

                    if index != length - 1:
                        self._move_exercise(index, length, e)
                case "save-reorder":
                    reordered_exercises = []

                    for list_item in self.parent.e_list.children:
                        exercise = list_item.children[0].exercise
                        reordered_exercises.append(exercise)

                    self.parent.exercises = reordered_exercises

                    routine = self.app.routines[self.parent.r_idx]
                    routine.exercises = reordered_exercises

                    save_routines(self.app.path, self.app.routines)

                    self.add_class("hide")
                case "cancel-reorder":
                    # Reset Exercise ListView
                    e_list: ListView = self.parent.e_list
                    e_list.remove_children()
                    e_list.extend(
                        [
                            ListItem(create_exercise_widget(e))
                            for e in self.parent.exercises
                        ]
                    )
                    self.add_class("hide")

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
        editing: bool = False,
    ) -> None:
        self.e_input.e_name.value = name
        self.e_input.duration_input.value = duration
        self.e_input.rep_input.value = rep
        self.e_input.e_type.value = type

        if editing:
            self.e_input.add_class("editing-exercise")
        elif self.e_input.has_class("editing-exercise"):
            self.e_input.remove_class("editing-exercise")

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
        self.reorder_input = self.ReorderWidget(classes="hide")
        yield self.reorder_input

    def action_add_exercise(self) -> None:
        self._show_exercise_form()

    def action_remove_exercise(self) -> None:
        selected_item = self.e_list.highlighted_child

        if selected_item is None or not self.e_list.has_focus:
            self.app.notify(
                message="Please select an exercise first.",
                title="Cannot Remove Exercise",
                severity="warning",
            )
            return

        self.e_list.remove_children([selected_item])

        routine: Routine = self.app.routines[self.r_idx]
        routine.exercises.pop(self.e_list.index)

        save_routines(self.app.path, self.app.routines)

    def action_edit_exercise(self) -> None:
        selected_item = self.e_list.highlighted_child

        if selected_item is None or not self.e_list.has_focus:
            self.app.notify(
                message="Please select an exercise first.",
                title="Cannot Edit Exercise",
                severity="warning",
            )
            return

        routine: Routine = self.app.routines[self.r_idx]
        e = routine.exercises[self.e_list.index]
        self.exercise_to_edit = e
        self.exercise_to_edit_idx = self.e_list.index
        self.exercise_to_edit_widget = selected_item
        if isinstance(e, DurationExercise):
            self._show_exercise_form(
                name=e.name,
                duration=e.duration_mask_string(),
                type=DURATION_OPTION,
                editing=True,
            )
        elif isinstance(e, RepetitionExercise):
            self._show_exercise_form(
                name=e.name,
                rep=str(e.repetitions),
                type=REPETITION_OPTION,
                editing=True,
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "reorder-btn":
            if self.reorder_input.has_class("hide"):
                self.reorder_input.remove_class("hide")
        elif button_id == "start-btn":
            self.app.switch_screen(TimerScreen(r_idx=self.r_idx))


class TimerScreen(Screen):
    CSS_PATH = "widgets/_timer.tcss"

    def __init__(self, r_idx: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.routine_idx = r_idx
        self.routine = self.app.routines[r_idx]
        self.exercise_iter = iter(self.routine.exercises)

    def handle_next_exercise(self):
        e = next(self.exercise_iter, None)
        if not e:
            from screens.routine_view import RoutineViewScreen

            self.app.switch_screen(RoutineViewScreen(self.routine_idx))
            return

        if isinstance(e, DurationExercise):
            self.rep_widget.add_class("hide")
            self.timer.remove_class("hide")
            self.timer.change_duration_time(e.duration)
        elif isinstance(e, RepetitionExercise):
            self.timer.add_class("hide")
            self.rep_widget.remove_class("hide")
            label = self.rep_widget.query_one(Label)
            label.update(f"{e.name} \n Repetitions: {e.repetitions}")

    def display_next_exercise(self, time_to_display: float) -> None:
        if time_to_display != 0.0:
            return

        self.handle_next_exercise()
        # self.timer.add_class("hide")
        # self.rep_widget.remove_class("hide")

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        self.timer = Timer(duration_time=5.0, id="exercise-timer")
        yield self.timer

        self.rep_widget = VerticalGroup(
            Label("Repetition Widget"),
            Button("Next", id="next-exercise", variant="primary"),
        )
        self.rep_widget.add_class("hide")
        yield self.rep_widget

    def on_mount(self) -> None:
        self.handle_next_exercise()
        self.watch(
            self.query_one("TimeDisplay"),
            "time_to_display",
            self.display_next_exercise,
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "next-exercise":
            self.handle_next_exercise()


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
        self.screen_manager = ScreenManager(self)

    def action_go_home(self) -> None:
        self.app.switch_screen("start")


if __name__ == "__main__":
    app = TimeroApp()
    app.run()
