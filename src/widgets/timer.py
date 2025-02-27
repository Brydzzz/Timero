from time import monotonic

from textual.app import ComposeResult
from textual.containers import Container, VerticalGroup
from textual.reactive import reactive
from textual.widgets import Button, Digits


class TimeDisplay(Digits):
    """A widget to display elapsed time."""

    CSS_PATH = "_timer.tcss"

    start_time = reactive(monotonic)
    time_to_display = reactive(0.0)
    time_left = reactive(0.0)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(
            1 / 60, self.update_time, pause=True
        )
        self.time_to_display = self.parent.duration_time
        self.time_left = self.parent.duration_time

    def update_time(self) -> None:
        self.time_to_display = max(
            0.0, self.time_left - (monotonic() - self.start_time)
        )

    def watch_time_to_display(self, time: float) -> None:
        if time == 0.0:
            self.update_timer.pause()
            self.parent.remove_class("started")
        time = max(0.0, time)
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")

    def start(self) -> None:
        """Method to start (or resume) time updating."""
        self.start_time = monotonic()
        self.update_timer.resume()

    def stop(self) -> None:
        """Method to stop the time display updating."""
        self.update_timer.pause()
        self.time_left -= monotonic() - self.start_time
        self.time_to_display = self.time_left

    def reset(self) -> None:
        """Method to reset the time display to zero."""
        self.time_left = self.parent.duration_time
        self.time_to_display = self.parent.duration_time


class Timer(VerticalGroup):
    """A timer widget."""

    def __init__(self, duration_time: float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.duration_time = duration_time

    def change_duration_time(self, new_time: float):
        self.duration_time = new_time
        time_display = self.query_one(TimeDisplay)
        time_display.time_left = self.duration_time
        time_display.time_to_display = self.duration_time

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if button_id == "start":
            time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif button_id == "reset":
            time_display.reset()

    def compose(self) -> ComposeResult:
        """Create child widgets of a timer."""
        yield TimeDisplay()
        yield Container(
            Button("Start", id="start", variant="success"),
            Button("Stop", id="stop", variant="error"),
            Button("Resetuj", id="reset"),
            id="timer-btn-container",
        )
