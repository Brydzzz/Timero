from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Label, Header, Footer, Button
from textual.containers import VerticalGroup
from routine import DurationExercise, RepetitionExercise
from widgets.timer import Timer


class TimerView(Screen):
    CSS_PATH = "widgets/timer.tcss"

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
