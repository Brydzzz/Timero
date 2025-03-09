from time import monotonic

from textual.app import ComposeResult
from textual.containers import Container, VerticalGroup
from textual.reactive import reactive
from textual.widgets import Button, Digits, Label
from textual.message import Message


TIMER_END_SOUND = "timer-end-sound.wav"
TIMER_START_SOUND = "timer-start-sound.wav"


class TimeDisplay(Digits):
    """A widget to display elapsed time."""

    CSS_PATH = "_timer.tcss"

    start_time = reactive(monotonic)
    time_to_display = reactive(0.0)
    time_left = reactive(0.0)

    class Ended(Message):
        """Timer ended message."""

        def __init__(self, time_display: "TimeDisplay") -> None:
            self.time_display: TimeDisplay = time_display
            super().__init__()

        @property
        def control(self) -> "TimeDisplay":
            return self.time_display

    def __init__(self, duration_time, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.duration_time = duration_time

    def _format_time(self, time: float) -> str:
        """Format time value into display string."""
        time = max(0.0, time)
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}"

    def on_mount(self) -> None:
        self.update_timer = self.set_interval(
            1 / 60, self.update_time, pause=True
        )
        self.set_reactive(TimeDisplay.time_to_display, self.duration_time)
        self.set_reactive(TimeDisplay.time_left, self.duration_time)
        self.update(self._format_time(self.duration_time))

    def update_time(self) -> None:
        self.time_to_display = max(
            0.0, self.time_left - (monotonic() - self.start_time)
        )

    def watch_time_to_display(self, time: float) -> None:
        if time == 0.0:
            self.update_timer.pause()
            self.parent.remove_class("started")
            self.app.sound_manager.play_sound(TIMER_END_SOUND)
            self.post_message(TimeDisplay.Ended(self))
        self.update(self._format_time(time))

    def start(self) -> None:
        """Method to start (or resume) time updating."""
        self.start_time = monotonic()
        self.update_timer.resume()
        self.app.sound_manager.play_sound(TIMER_START_SOUND)

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

    def __init__(self, title: str, duration_time: float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.duration_time = duration_time
        self.title = title

    def change_duration_time(self, new_time: float):
        self.duration_time = new_time
        time_display = self.query_one(TimeDisplay)
        time_display.time_left = self.duration_time
        time_display.time_to_display = self.duration_time

    def on_button_pressed(self, event: Button.Pressed) -> None:
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
        yield Container(
            Label(self.title, id="timer-title"), id="title-container"
        )
        yield TimeDisplay(self.duration_time)
        yield Container(
            Button("Start", id="start", variant="success"),
            Button("Stop", id="stop", variant="error"),
            Button("Reset", id="reset"),
            id="timer-btn-container",
        )

    def _start_timer_safe(self) -> None:
        time_display = self.query_one(TimeDisplay)
        time_display.start()
        self.add_class("started")

    def start_timer(self) -> None:
        self.call_after_refresh(self._start_timer_safe)

    def stop_timer(self) -> None:
        time_display = self.query_one(TimeDisplay)
        time_display.stop()

    def reset_timer(self) -> None:
        time_display = self.query_one(TimeDisplay)
        time_display.reset()
