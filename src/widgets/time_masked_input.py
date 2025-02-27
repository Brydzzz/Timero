from textual.widgets import MaskedInput
from validators import IsEmptyValidator, TimeValidator


class TimeMaskedInput(MaskedInput):
    def __init__(self, *args, **kwargs):
        kwargs.update(
            {
                "template": "99:99:99;0",
                "placeholder": "HH:MM:SS",
                "validators": [TimeValidator(), IsEmptyValidator()],
            }
        )
        super().__init__(*args, **kwargs)
