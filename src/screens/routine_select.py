from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, ListItem, ListView, Label


class RoutinesSelectScreen(Screen):
    """Screen with all routines"""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        items = (
            ListItem(Label(r.name), name=str(idx))
            for idx, r in enumerate(self.app.routines)
        )
        lv = ListView(*items, classes="routines-list")
        lv.border_title = "Select Routine: "
        yield lv

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        idx = int(event.item.name)
        self.app.routine_controller.set_routine(self.app.routines[idx])
        self.app.screen_manager.go_to_routine()
