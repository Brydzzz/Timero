from textual.validation import Validator, ValidationResult


class IsEmptyValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        return (
            self.success() if len(value) != 0 else self.failure("Empty Input")
        )


class TimeValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        cleaned = value.replace(":", "")

        if len(cleaned) < 6:
            return self.failure("Input too short")

        if len(cleaned) >= 4:
            minutes = int(cleaned[2:4])
            if minutes > 59:
                return self.failure("Minutes must be 00-59")

        if len(cleaned) >= 6:
            seconds = int(cleaned[4:6])
            if seconds > 59:
                return self.failure("Seconds must be 00-59")

        return self.success()
