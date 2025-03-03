from textual import on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Button, ProgressBar
from routine import DurationExercise, RepetitionExercise
from widgets.timer import TimeDisplay, Timer
from widgets.train_repetition import TrainRepetitionWidget


class TrainView(Screen):
    CSS_PATH = "../widgets/timer.tcss"

    BINDINGS = [("s", "skip_exercise", "Skip")]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.routine = self.app.routines[self.app.curr_routine_idx]
        self.exercise_iter = iter(self.routine.exercises)
        self.total_exercises = len(self.routine.exercises)
        self.completed_exercises = 0

    def _remove_train_widgets(self) -> None:
        children = self.query_children()
        train_widgets = children.exclude(".no-remove")
        self.remove_children(train_widgets)

    def start_break_timer(self) -> None:
        if self.total_exercises == self.completed_exercises:
            self.app.screen_manager.go_to_routine()
            # TODO: switch to end screen or notify user?
            return
        self._remove_train_widgets()
        self.break_timer.reset_timer()
        self.break_timer.remove_class("hide")

    def update_progress(self) -> None:
        self.completed_exercises += 1
        self.progress_bar.update(
            progress=(self.completed_exercises / self.total_exercises) * 100
        )

    def handle_next_exercise(self):
        self._remove_train_widgets()
        e = next(self.exercise_iter, None)
        if not e:
            self.app.screen_manager.go_to_routine()
            # TODO: switch to end screen or notify user?
            return

        if isinstance(e, DurationExercise):
            timer_widget = Timer(
                title=e.name,
                duration_time=e.duration,
                classes="exercise-timer",
            )
            self.mount(timer_widget)
        elif isinstance(e, RepetitionExercise):
            train_widget = TrainRepetitionWidget(e)
            self.mount(train_widget)

    def compose(self) -> ComposeResult:
        yield Header(classes="no-remove")
        self.progress_bar = ProgressBar(
            classes="no-remove",
            total=100,
            show_eta=False,
        )
        yield self.progress_bar
        BREAK_DURATION = 7  # TODO: in future value from user settings
        self.break_timer = Timer(
            title="Break",
            duration_time=BREAK_DURATION,
            id="break-timer",
            classes="no-remove hide",
        )
        yield self.break_timer
        yield Footer(classes="no-remove")

    def on_mount(self) -> None:
        self.handle_next_exercise()

    @on(TimeDisplay.Ended, ".exercise-timer TimeDisplay")
    def exercise_timer_ended(self) -> None:
        self.update_progress()
        self.start_break_timer()

    @on(TimeDisplay.Ended, "#break-timer TimeDisplay")
    def break_timer_ended(self) -> None:
        self.break_timer.add_class("hide")
        self.handle_next_exercise()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "reps-finished":
            self.update_progress()
            self.start_break_timer()

    def action_skip_exercise(self):
        if self.break_timer.has_class("hide"):
            self.update_progress()
            self.start_break_timer()
        else:
            self.break_timer.add_class("hide")
            self.handle_next_exercise()
