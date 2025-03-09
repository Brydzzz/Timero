from textual.app import App

from routine import (
    DurationExercise,
    RepetitionExercise,
    Routine,
)


class RoutineController:
    def __init__(self, app):
        self.app: App = app
        self.routine: Routine = None

    def set_routine(self, routine: Routine) -> None:
        self.routine = routine

    def get_routine_name(self) -> str:
        return self.routine.name

    def get_exercises(self) -> list[RepetitionExercise | DurationExercise]:
        return self.routine.exercises

    def add_exercise(self, exercise) -> None:
        if self.routine:
            self.routine.add_exercise(exercise)
            self._save_routines(self.app.routines)

    def remove_exercise(self, exercise_idx):
        if self.routine and exercise_idx < len(self.routine.exercises):
            self.routine.exercises.pop(exercise_idx)
            self._save_routines(self.app.routines)

    def update_exercise(self, exercise_idx, exercise):
        if self.routine and exercise_idx < len(self.routine.exercises):
            self.routine.exercises[exercise_idx] = exercise
            self._save_routines(self.app.routines)

    def replace_exercise(self, exercise, exercise_idx):
        if self.routine:
            self.routine.replace_exercise(exercise, exercise_idx)
            self._save_routines(self.app.routines)

    def reorder_exercises(
        self, new_order: list[RepetitionExercise | DurationExercise]
    ):
        if self.routine:
            self.routine.exercises = new_order
            self._save_routines(self.app.routines)

    def load_routines(self):
        from routine import load_routines

        return load_routines(self.app.routines_path)

    def _save_routines(self, routines):
        from routine import save_routines

        save_routines(self.app.routines_path, routines)
