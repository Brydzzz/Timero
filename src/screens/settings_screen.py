from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Switch, Input, Button, Label
from textual.containers import (
    VerticalScroll,
    HorizontalGroup,
    Middle,
)

from validators import IsEmptyValidator


class SettingsScreen(Screen):
    CSS_PATH = "settings_screen.tcss"

    def compose(self) -> ComposeResult:
        yield Header()

        with VerticalScroll():
            with HorizontalGroup(classes="settings-item-container"):
                with Middle():
                    yield Label(
                        "Show breaks between exercises",
                        classes="setting-label",
                    )
                with Middle():
                    yield Switch(
                        value=self.app.settings.get("show_breaks"),
                        id="show-breaks-switch",
                    )

            with HorizontalGroup(classes="settings-item-container"):
                with Middle():
                    yield Label(
                        "Auto start break timers", classes="setting-label"
                    )
                with Middle():
                    yield Switch(
                        value=self.app.settings.get("auto_start_breaks"),
                        id="auto-start-breaks-switch",
                    )

            with HorizontalGroup(classes="settings-item-container"):
                with Middle():
                    yield Label(
                        "Auto start exercise timers", classes="setting-label"
                    )
                with Middle():
                    yield Switch(
                        value=self.app.settings.get("auto_start_exercises"),
                        id="auto-start-exercises-switch",
                    )

            with HorizontalGroup(classes="settings-item-container"):
                with Middle():
                    yield Label(
                        "Break duration (in seconds)", classes="setting-label"
                    )
                yield Input(
                    value=str(self.app.settings.get("break_duration")),
                    id="break-duration-input",
                    type="integer",
                    validators=[IsEmptyValidator()],
                )

            with HorizontalGroup(id="buttons-container"):
                yield Button("Save", id="save-settings", variant="success")
                yield Button("Reset to Defaults", id="reset-settings")
                yield Button("Cancel", id="cancel-settings", variant="error")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "save-settings":
            self.save_settings()
        elif button_id == "reset-settings":
            self.app.settings.reset_to_defaults()
            self.update_form_values()
        elif button_id == "cancel-settings":
            self.app.switch_screen("homepage")

    def save_settings(self) -> None:
        if not self.query_one("#break-duration-input").is_valid:
            self.notify(
                message="Break duration cannot be empty",
                title="Cannot Save Settings",
                severity="error",
            )
            return
        show_breaks = self.query_one("#show-breaks-switch").value
        auto_start_breaks = self.query_one("#auto-start-breaks-switch").value
        auto_start_exercises = self.query_one(
            "#auto-start-exercises-switch"
        ).value
        break_duration = int(self.query_one("#break-duration-input").value)

        self.app.settings.set("show_breaks", show_breaks)
        self.app.settings.set("auto_start_breaks", auto_start_breaks)
        self.app.settings.set("auto_start_exercises", auto_start_exercises)
        self.app.settings.set("break_duration", break_duration)
        self.app.settings.save_settings()

        self.app.switch_screen("homepage")

    def update_form_values(self) -> None:
        self.query_one("#show-breaks-switch").value = self.app.settings.get(
            "show_breaks"
        )
        self.query_one("#auto-start-breaks-switch").value = (
            self.app.settings.get("auto_start_breaks")
        )
        self.query_one("#auto-start-exercises-switch").value = (
            self.app.settings.get("auto_start_exercises")
        )
        self.query_one("#break-duration-input").value = str(
            self.app.settings.get("break_duration")
        )
