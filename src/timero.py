from pathlib import Path
from textual.app import App
from textual.reactive import reactive, var


from routine import Routine
from screens.homepage import Homepage

from screens.screen_manager import ScreenManager
from screens.settings_screen import SettingsScreen
from settings import Settings
from sound_manager import SoundManager


class TimeroApp(App):
    CSS_PATH = "timero.tcss"
    BINDINGS = [
        ("h", "go_home", "Homepage"),
        ("ctrl+s", "open_settings", "Settings"),
    ]

    routines: list[Routine] = reactive(None)
    path = var(Path(__file__).parent.parent / "routines.json")
    curr_routine_idx = var(0)

    def on_mount(self) -> None:
        self.install_screen(Homepage(id="homepage"), name="homepage")
        self.install_screen(SettingsScreen(id="settings"), name="settings")
        self.push_screen("homepage")
        self.theme = "gruvbox"
        self.screen_manager = ScreenManager(self)
        self.sound_manager = SoundManager(
            Path(__file__).parent.parent / "assets" / "audio"
        )
        self.settings = Settings(Path(__file__).parent.parent / "config.json")

    def action_go_home(self) -> None:
        self.app.switch_screen("homepage")

    def action_open_settings(self) -> None:
        self.app.switch_screen("settings")

    def on_exit(self):
        self.sound_manager.quit()


if __name__ == "__main__":
    app = TimeroApp()
    app.run()
