from textual.containers import VerticalGroup
from textual.app import ComposeResult
from textual.widgets import Label, Button
from rich.text import Text
from routine import RepetitionExercise


class TrainRepetitionWidget(VerticalGroup):

    DEFAULT_CSS = """
        TrainRepetitionWidget {
            background: $boost;
            align: center middle;
            width: auto;
            padding: 2 4;
        }


        #rep-exercise-name {
            text-style: bold;
            border: ascii $border;
            padding: 0 2;
            text-align: center;
        }
    """

    def __init__(
        self, exercise: RepetitionExercise | None = None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.exercise = exercise or RepetitionExercise(
            name="Unknown", repetitions=0
        )

    def change_exercise(self, exercise: RepetitionExercise) -> None:
        self.exercise = exercise
        self.query_one("#rep-exercise-name", Label).update(self.exercise.name)
        self.query_one("#repetitions-count-label", Label).update(
            Text(f"Repetitions: {self.exercise.repetitions}")
        )

    def compose(self) -> ComposeResult:
        yield Label(self.exercise.name, id="rep-exercise-name")
        yield Label(
            Text(f"Repetitions: {self.exercise.repetitions}"),
            id="repetitions-count-label",
        )
        yield Button("Finished", id="reps-finished", variant="success")

    def on_mount(self) -> None:
        self.query_one("#reps-finished", Button).focus()
