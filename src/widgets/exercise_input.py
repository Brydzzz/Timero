from textual.containers import HorizontalGroup
from textual.app import ComposeResult
from textual.widgets import Input, Select, Button, ListItem
from textual import log
from widgets.exercises import create_exercise_widget
from widgets.time_masked_input import TimeMaskedInput

from routine import (
    DurationExercise,
    RepetitionExercise,
    Routine,
    save_routines,
)
from utils import duration_input_to_seconds
from validators import IsEmptyValidator

DURATION_OPTION = 1
REPETITION_OPTION = 2


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

            routine: Routine = self.app.routines[self.app.curr_routine_idx]
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
            routine: Routine = self.app.routines[self.app.curr_routine_idx]

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
