from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Button
from routine import DurationExercise, RepetitionExercise
from widgets.timer import TimeDisplay, Timer
from widgets.train_repetition import TrainRepetitionWidget


class TrainView(Screen):
    CSS_PATH = "../widgets/timer.tcss"

    BINDINGS = [("s", "skip_exercise", "Skip Exercise")]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.routine = self.app.routines[self.app.curr_routine_idx]
        self.exercise_iter = iter(self.routine.exercises)

    def handle_next_exercise(self):
        e = next(self.exercise_iter, None)
        if not e:
            self.app.screen_manager.go_to_routine()
            return

        children = self.query_children()
        train_widgets = children.exclude(".no-remove")
        self.remove_children(train_widgets)

        if isinstance(e, DurationExercise):
            timer_widget = Timer(
                title=e.name, duration_time=e.duration, id="exercise-timer"
            )
            self.mount(timer_widget)
        elif isinstance(e, RepetitionExercise):
            train_widget = TrainRepetitionWidget(e)
            self.mount(train_widget)

    def compose(self) -> ComposeResult:
        yield Header(classes="no-remove")
        yield Footer(classes="no-remove")

    def on_mount(self) -> None:
        self.handle_next_exercise()

    def on_time_display_ended(self, event: TimeDisplay.Ended) -> None:
        self.handle_next_exercise()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "reps-finished":
            self.handle_next_exercise()
        elif button_id == "skip-exercise":
            self.handle_next_exercise()

    def action_skip_exercise(self):
        self.handle_next_exercise()
