import json


class Exercise:
    def __init__(self, name: str):
        self.name = name


class DurationExercise(Exercise):
    def __init__(self, name: str, duration: int):
        super().__init__(name)
        self.duration = duration

    def duration_mask_string(self) -> str:
        minutes, sec = divmod(self.duration, 60)
        hours, minutes = divmod(minutes, 60)
        parts = []
        parts.append(f"{hours:02}")
        parts.append(f"{minutes:02}")
        parts.append(f"{sec:02}")

        return ":".join(parts)


class RepetitionExercise(Exercise):
    def __init__(self, name: str, repetitions: int):
        super().__init__(name)
        self.repetitions = repetitions


class Routine:
    def __init__(self, name: str, exercises: Exercise = None):
        self.name = name
        self.exercises = exercises if exercises else []

    def add_exercise(self, exercise: Exercise):
        self.exercises.append(exercise)

    def replace_exercise(self, new_exercise: Exercise, idx: int):
        self.exercises[idx] = new_exercise


class RoutineEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Routine):
            return {
                "__type__": "Routine",
                "name": obj.name,
                "exercises": obj.exercises,
            }
        elif isinstance(obj, DurationExercise):
            return {
                "__type__": "DurationExercise",
                "name": obj.name,
                "duration": obj.duration,
            }
        elif isinstance(obj, RepetitionExercise):
            return {
                "__type__": "RepetitionExercise",
                "name": obj.name,
                "repetitions": obj.repetitions,
            }
        return super().default(obj)


class RoutineDecoder(json.JSONDecoder):
    def __init__(self):
        super().__init__(object_hook=self.object_hook)

    def object_hook(self, obj):
        if "__type__" in obj:
            if obj["__type__"] == "Routine":
                routine = Routine(obj["name"])
                routine.exercises = obj["exercises"]
                return routine
            elif obj["__type__"] == "DurationExercise":
                return DurationExercise(obj["name"], obj["duration"])
            elif obj["__type__"] == "RepetitionExercise":
                return RepetitionExercise(obj["name"], obj["repetitions"])
        return obj


def save_routines(filename, routines):
    with open(filename, "w") as file:
        json.dump(routines, file, cls=RoutineEncoder, indent=2)


def load_routines(filename):
    with open(filename, "r") as file:
        return json.load(file, cls=RoutineDecoder)


if __name__ == "__main__":
    routine1 = Routine("Morning Workout")
    routine1.add_exercise(DurationExercise("Plank", 60))
    routine1.add_exercise(RepetitionExercise("Push-ups", 15))

    routine2 = Routine("Evening Routine")
    routine2.add_exercise(RepetitionExercise("Jump Rope", 30))

    save_routines("routines.json", [routine1, routine2])

    loaded_routines = load_routines("routines.json")
    for r in loaded_routines:
        print(r)
