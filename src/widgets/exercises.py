from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.widgets import Label
from routine import DurationExercise, RepetitionExercise, Exercise

from utils import (
    repetitions_to_str,
    seconds_to_time_str,
)


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


def create_exercise_widget(e: Exercise) -> ExerciseWidget:
    if isinstance(e, DurationExercise):
        return DurationExerciseWidget(e, e.name, e.duration)
    elif isinstance(e, RepetitionExercise):
        return RepetitionExerciseWidget(e, e.name, e.repetitions)
