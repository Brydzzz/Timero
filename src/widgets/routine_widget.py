from textual import on
from textual.app import ComposeResult
from textual.containers import HorizontalGroup

from textual.reactive import reactive
from textual.widgets import (
    Button,
    Label,
    ListView,
    ListItem,
)

from routine import (
    DurationExercise,
    Exercise,
    RepetitionExercise,
)


from screens.train_view import TrainView
from widgets.exercise_input import (
    DURATION_OPTION,
    REPETITION_OPTION,
    ExerciseInputWidget,
)
from widgets.exercises import create_exercise_widget


class ReorderWidget(HorizontalGroup):

    def compose(self) -> ComposeResult:
        yield Button("🔼", id="move-up", classes="icon-btn")
        yield Button("⏫", id="move-top", classes="icon-btn")
        yield Button("🔽", id="move-down", classes="icon-btn")
        yield Button("⏬", id="move-bottom", classes="icon-btn")
        yield Button("Save", id="save-reorder")
        yield Button("Cancel", id="cancel-reorder", variant="error")

    def _get_exercise_to_move(self) -> tuple[int, Exercise]:
        e_list: ListView = self.parent.e_list
        index = e_list.index
        item: ListItem = e_list.highlighted_child
        e_widget = item.query_one(".exercise-widget")
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

    def _save_reordered_exercises(self):
        reordered_exercises = []

        for list_item in self.parent.e_list.children:
            exercise = list_item.children[0].exercise
            reordered_exercises.append(exercise)

        self.app.routine_controller.reorder_exercises(reordered_exercises)

    def _reset_exercise_list(self):
        e_list: ListView = self.parent.e_list
        e_list.remove_children()
        e_list.extend(
            [
                ListItem(create_exercise_widget(e))
                for e in self.app.routine_controller.get_exercises()
            ]
        )

    @on(Button.Pressed, "#move-up")
    def move_exercise_one_up(self):
        index, e = self._get_exercise_to_move()
        if index > 0:
            self._move_exercise(index, index - 1, e)

    @on(Button.Pressed, "#move-top")
    def move_exercise_to_the_top(self):
        index, e = self._get_exercise_to_move()
        if index != 0:
            self._move_exercise(index, 0, e)

    @on(Button.Pressed, "#move-down")
    def move_exercise_one_down(self):
        index, e = self._get_exercise_to_move()
        e_list: ListView = self.parent.e_list
        if index < len(e_list.children) - 1:
            self._move_exercise(index, index + 2, e)

    @on(Button.Pressed, "#move-bottom")
    def move_exercise_to_the_bottom(self):
        index, e = self._get_exercise_to_move()
        length = len(self.parent.e_list.children)
        if index != length - 1:
            self._move_exercise(index, length, e)

    @on(Button.Pressed, "#save-reorder")
    def save_reorder(self):
        self._save_reordered_exercises()
        self.add_class("hide")

    @on(Button.Pressed, "#cancel-reorder")
    def cancel_reorder(self):
        self._reset_exercise_list()
        self.add_class("hide")


class RoutineWidget(HorizontalGroup):

    BINDINGS = [
        ("a", "add_exercise", "Add Exercise"),
        ("r", "remove_exercise", "Remove Exercise"),
        ("e", "edit_exercise", "Edit Exercise"),
    ]

    # Accessed by exercise input
    exercise_to_edit: DurationExercise | RepetitionExercise = reactive(None)
    exercise_to_edit_idx: int = reactive(None)
    exercise_to_edit_widget = reactive(None)

    def _clear_exercise_form(self) -> None:
        self.e_input.e_name.value = ""
        self.e_input.duration_input.value = ""
        self.e_input.rep_input.value = ""
        self.e_input.e_type.value = DURATION_OPTION

    def _fill_exercise_form_with_exercise_data(self, exercise) -> None:
        if exercise.type == "duration":
            self.e_input.e_name.value = exercise.name
            self.e_input.duration_input.value = exercise.duration_mask_string()
            self.e_input.rep_input.value = ""
            self.e_input.e_type.value = DURATION_OPTION
        elif exercise.type == "repetition":
            self.e_input.e_name.value = exercise.name
            self.e_input.duration_input.value = ""
            self.e_input.rep_input.value = str(exercise.repetitions)
            self.e_input.e_type.value = REPETITION_OPTION
        else:
            self.log("Exercise type unknown")

    def _show_exercise_form(
        self,
        exercise=None,
        editing: bool = False,
    ) -> None:
        if exercise:
            self._fill_exercise_form_with_exercise_data(exercise)
        else:
            self._clear_exercise_form()

        if editing:
            self.e_input.add_class("editing-exercise")
        elif self.e_input.has_class("editing-exercise"):
            self.e_input.remove_class("editing-exercise")

        self.e_input.remove_class("hide")
        self.e_input.e_name.focus()

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(
            Label(
                self.app.routine_controller.get_routine_name(),
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
            *[
                ListItem(create_exercise_widget(e))
                for e in self.app.routine_controller.get_exercises()
            ],
            id="exercises-scroll",
        )
        yield self.e_list

        self.reorder_input = ReorderWidget(classes="hide")
        yield self.reorder_input

    def action_add_exercise(self) -> None:
        self._show_exercise_form()

    def action_remove_exercise(self) -> None:
        selected_item = self.e_list.highlighted_child

        if not (selected_item and self.e_list.has_focus):
            self.app.notify(
                message="Please select an exercise first.",
                title="Cannot Remove Exercise",
                severity="warning",
            )
            return

        self.e_list.remove_children([selected_item])
        self.app.routine_controller.remove_exercise(self.e_list.index)

    def action_edit_exercise(self) -> None:
        selected_item = self.e_list.highlighted_child

        if not (selected_item and self.e_list.has_focus):
            self.app.notify(
                message="Please select an exercise first.",
                title="Cannot Edit Exercise",
                severity="warning",
            )
            return

        e = self.app.routine_controller.get_exercises()[self.e_list.index]
        self.exercise_to_edit = e
        self.exercise_to_edit_idx = self.e_list.index
        self.exercise_to_edit_widget = selected_item
        self._show_exercise_form(e, editing=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "reorder-btn":
            if len(self.app.routine_controller.get_exercises()) == 0:
                self.notify(
                    title="Failed to reorder routine's exercises",
                    message="Exercise list can't be empty",
                    severity="error",
                )
                return
            if self.reorder_input.has_class("hide"):
                self.reorder_input.remove_class("hide")
        elif button_id == "start-btn":
            if len(self.app.routine_controller.get_exercises()) == 0:
                self.notify(
                    title="Failed to start routine",
                    message="Exercise list can't be empty",
                    severity="error",
                )
                return
            self.app.switch_screen(TrainView())
