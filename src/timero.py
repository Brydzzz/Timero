from pathlib import Path
from textual.app import App
from textual.reactive import reactive, var


from routine import Routine
from screens.homepage import Homepage

from screens.screen_manager import ScreenManager
from sound_manager import SoundManager


class TimeroApp(App):
    CSS_PATH = "timero.tcss"
    BINDINGS = [("h", "go_home", "Homepage")]

    routines: list[Routine] = reactive(None)
    path = var(Path(__file__).parent.parent / "routines.json")
    curr_routine_idx = var(0)

    def on_mount(self) -> None:
        self.install_screen(Homepage(id="start"), name="start")
        self.push_screen("start")
        self.theme = "gruvbox"
        self.screen_manager = ScreenManager(self)
        self.sound_manager = SoundManager(
            Path(__file__).parent.parent / "assets" / "audio"
        )

    def action_go_home(self) -> None:
        self.app.switch_screen("start")

    def on_exit(self):
        self.sound_manager.quit()


if __name__ == "__main__":
    app = TimeroApp()
    app.run()
