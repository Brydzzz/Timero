from textual.app import App


class ScreenManager:
    def __init__(self, app: App):
        self.app = app

    def go_to_routine(self, r_idx: int):
        from screens.routine_view import RoutineViewScreen

        self.app.switch_screen(RoutineViewScreen(r_idx=r_idx))

    def go_to_routine_select(self):
        from screens.routine_select import RoutinesSelectScreen

        self.app.switch_screen(RoutinesSelectScreen())
