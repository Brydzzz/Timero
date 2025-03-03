from pathlib import Path
from textual.app import App
from textual.reactive import reactive, var


from routine import Routine
from screens.start import StartScreen

from screens.manager import ScreenManager


class TimeroApp(App):
    CSS_PATH = "timero.tcss"
    BINDINGS = [("h", "go_home", "Homepage")]

    routines: list[Routine] = reactive(None)
    path = var(Path(__file__).parent.parent / "routines.json")
    curr_routine_idx = var(0)

    def on_mount(self) -> None:
        self.install_screen(StartScreen(id="start"), name="start")
        self.push_screen("start")
        self.theme = "gruvbox"
        self.screen_manager = ScreenManager(self)

    def action_go_home(self) -> None:
        self.app.switch_screen("start")


if __name__ == "__main__":
    app = TimeroApp()
    app.run()
