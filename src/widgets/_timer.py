from time import monotonic

from textual.app import ComposeResult
from textual.containers import Container, VerticalGroup
from textual.reactive import reactive
from textual.widgets import Button, Digits


class TimeDisplay(Digits):
    """A widget to display elapsed time."""

    CSS_PATH = "_timer.tcss"

    start_time = reactive(monotonic)
    time = reactive(5.0)
    total = reactive(5.0)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(
            1 / 60, self.update_time, pause=True
        )

    def update_time(self) -> None:
        self.time = max(0.0, self.total - (monotonic() - self.start_time))
        if self.time == 0.0:
            self.update_timer.pause()
            self.parent.remove_class("started")

    def watch_time(self, time: float) -> None:
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
        self.total -= monotonic() - self.start_time
        self.time = self.total

    def reset(self) -> None:
        """Method to reset the time display to zero."""
        self.total = 5.0
        self.time = 5.0


class Timer(VerticalGroup):
    """A timer widget."""

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
