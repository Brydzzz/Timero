from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup
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

from screens.start import StartScreen
from routine import (
    DurationExercise,
    Exercise,
    RepetitionExercise,
    Routine,
    save_routines,
)

from screens.manager import ScreenManager

from screens.timer_view import TimerView
from widgets.exercise_input import (
    DURATION_OPTION,
    REPETITION_OPTION,
    ExerciseInputWidget,
)
from widgets.exercises import create_exercise_widget


class RoutineWidget(HorizontalGroup):

    BINDINGS = [
        ("a", "add_exercise", "Add Exercise"),
        ("r", "remove_exercise", "Remove Exercise"),
        ("e", "edit_exercise", "Edit Exercise"),
    ]

    exercise_to_edit: DurationExercise | RepetitionExercise = reactive(None)
    exercise_to_edit_idx: int = reactive(None)
    exercise_to_edit_widget = reactive(None)

    class ReorderWidget(HorizontalGroup):

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
            self.app.switch_screen(TimerView(r_idx=self.r_idx))


class TimeroApp(App):
    CSS_PATH = "timero.tcss"
    BINDINGS = [("h", "go_home", "Go to homepage")]

    routines: list[Routine] = reactive(None)
    path = var(Path(__file__).parent.parent / "routines.json")

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
