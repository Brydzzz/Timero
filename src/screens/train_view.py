from textual import on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Button, ProgressBar
from textual.reactive import reactive
from textual.css.query import NoMatches
from routine import DurationExercise, RepetitionExercise
from widgets.timer import TimeDisplay, Timer
from widgets.train_repetition import TrainRepetitionWidget
from widgets.training_end import TrainingEndWidget


class TrainView(Screen):
    CSS_PATH = "../widgets/timer.tcss"

    BINDINGS = [("s", "skip_exercise", "Skip")]

    is_in_break = reactive(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        exercises = self.app.routine_controller.get_exercises()
        self.exercise_iter = iter(exercises)
        self.total_exercises = len(exercises)
        self.show_breaks = self.app.settings.get("show_breaks")
        self.auto_start_breaks = self.app.settings.get("auto_start_breaks")
        self.auto_start_exercises = self.app.settings.get(
            "auto_start_exercises"
        )
        self.break_duration = self.app.settings.get("break_duration")
        self.completed_exercises = 0

    def _remove_train_widgets(self) -> None:
        children = self.query_children()
        train_widgets = children.exclude(".no-remove")
        self.remove_children(train_widgets)

    def _show_training_end(self) -> None:
        self._remove_train_widgets()
        self.mount(
            TrainingEndWidget(self.app.routine_controller.get_routine_name())
        )

    def _start_break_timer(self) -> None:
        self._remove_train_widgets()
        self.break_timer.reset_timer()
        self.break_timer.remove_class("hide")
        self.is_in_break = True
        if self.auto_start_breaks:
            self.break_timer.start_timer()

    def _update_progress_bar(self) -> None:
        progress_percent = (
            self.completed_exercises / self.total_exercises
        ) * 100
        self.progress_bar.update(progress=progress_percent)

    def _show_next_exercise(self):
        self._remove_train_widgets()
        e = next(self.exercise_iter, None)
        self.is_in_break = False

        if isinstance(e, DurationExercise):
            timer_widget = Timer(
                title=e.name,
                duration_time=e.duration,
                classes="exercise-timer",
            )
            self.mount(timer_widget)
            if self.auto_start_exercises:
                timer_widget.start_timer()
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
        self.break_timer = Timer(
            title="Break",
            duration_time=self.break_duration,
            id="break-timer",
            classes="no-remove hide",
        )
        yield self.break_timer
        yield Footer(classes="no-remove")

    def on_mount(self) -> None:
        self._show_next_exercise()

    def choose_next_action(self):
        if self.completed_exercises == self.total_exercises:
            self._update_progress_bar()
            self._show_training_end()
            return

        if self.show_breaks:
            if self.is_in_break:
                self.break_timer.add_class("hide")
                self._show_next_exercise()
            else:
                self._update_progress_bar()
                self._start_break_timer()
        else:
            self._update_progress_bar()
            self._show_next_exercise()

    @on(TimeDisplay.Ended, ".exercise-timer TimeDisplay")
    def exercise_timer_ended(self) -> None:
        self.completed_exercises += 1
        self.choose_next_action()

    @on(TimeDisplay.Ended, "#break-timer TimeDisplay")
    def break_timer_ended(self) -> None:
        self.choose_next_action()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "reps-finished":
            self.completed_exercises += 1
            self.choose_next_action()
        elif button_id == "exit-training":
            self.app.screen_manager.go_to_routine()

    def action_skip_exercise(self):
        if (
            not self.is_in_break
            and self.completed_exercises != self.total_exercises
        ):
            self.completed_exercises += 1

        if self.is_in_break:
            self.break_timer.stop_timer()
        try:
            self.query_one(".exercise-timer", Timer).stop_timer()
        except NoMatches:
            pass

        self.choose_next_action()
