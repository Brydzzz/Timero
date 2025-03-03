from textual.containers import VerticalGroup, Container
from textual.app import ComposeResult
from textual.widgets import Label, Button, Digits
from art import text2art
from routine import RepetitionExercise


class TrainRepetitionWidget(VerticalGroup):

    DEFAULT_CSS = """
        TrainRepetitionWidget {
            background: $boost;
            align: center middle;
            max-width: 55vw;
            max-height: 65vh;
            height: auto;
            margin: 1;
            padding: 1;
            content-align: center middle;
        }


        #exercise-name-container {
            align-horizontal: center;
            width: 100%;
        }

        #rep-exercise-name {
            text-style: bold;
            border: ascii $border;
            padding: 0 2;
            text-align: center;
        }

        #repetitions-number {
            text-align: center;
            text-style: bold;
            width: 100%;
            margin-top: 1;
        }

        #repetitions-label {
            text-align: center;
            width: 100%;
            margin: 0;
            padding: 0;
            height: 3;
            box-sizing: border-box;
        }

        #button-container {
            align-horizontal: center;
            width: 100%;
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
        self.query_one("#repetitions-number", Digits).update(
            f"{self.exercise.repetitions}"
        )

    def compose(self) -> ComposeResult:
        with Container(id="exercise-name-container"):
            yield Label(self.exercise.name, id="rep-exercise-name")
        yield Digits(f"{self.exercise.repetitions}", id="repetitions-number")
        yield Label(
            text2art("REPETITIONS", "straight"),
            id="repetitions-label",
        )
        with Container(id="button-container"):
            yield Button("Finished", id="reps-finished", variant="success")

    def on_mount(self) -> None:
        self.query_one("#reps-finished", Button).focus()
