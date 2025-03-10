from textual.app import App
import datetime
from routine import (
    DurationExercise,
    RepetitionExercise,
    Routine,
)


class RoutineController:
    def __init__(self, app):
        self.app: App = app
        self.routine: Routine = None

    def create_and_set_new_routine(self) -> None:
        x = datetime.datetime.now()
        self.routine = Routine(name=f"Routine-{x.strftime('%d-%m-%Y-%X')}")

    def check_if_routine_exists(self, routine_name: str) -> bool:
        for r in self.app.routines:
            if r.name == routine_name:
                return True
        return False

    def set_routine(self, routine: Routine) -> None:
        self.routine = routine

    def unset_routine(self) -> None:
        self.routine = None

    def set_routine_name(self, routine_name: Routine) -> bool:
        if self.check_if_routine_exists(routine_name):
            return False
        else:
            self.routine.name = routine_name
            return True

    def add_routine_to_app_routines(self):
        self.app.routines.append(self.routine)

    def get_routine_name(self) -> str:
        return self.routine.name

    def get_exercises(self) -> list[RepetitionExercise | DurationExercise]:
        return self.routine.exercises

    def add_exercise(self, exercise) -> None:
        if self.routine:
            self.routine.add_exercise(exercise)

    def remove_exercise(self, exercise_idx):
        if self.routine and exercise_idx < len(self.routine.exercises):
            self.routine.exercises.pop(exercise_idx)

    def update_exercise(self, exercise_idx, exercise):
        if self.routine and exercise_idx < len(self.routine.exercises):
            self.routine.exercises[exercise_idx] = exercise

    def replace_exercise(self, exercise, exercise_idx):
        if self.routine:
            self.routine.replace_exercise(exercise, exercise_idx)

    def reorder_exercises(
        self, new_order: list[RepetitionExercise | DurationExercise]
    ):
        if self.routine:
            self.routine.exercises = new_order

    def load_routines(self) -> list[Routine]:
        from routine import load_routines

        if not self.app.routines_path.exists():
            open(self.app.routines_path, "w").close()
            return []
        else:
            return load_routines(self.app.routines_path)

    def save_routines(self):
        from routine import save_routines

        save_routines(self.app.routines_path, self.app.routines)
