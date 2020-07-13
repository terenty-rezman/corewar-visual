from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QSizePolicy, QApplication
from PySide2.QtCore import Qt, QEvent


def update_stylesheet(widget):
    """
    dirty hack to force style recalc
    needed to react to changing properties
    """
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    evt = QEvent(QEvent.StyleChange)
    QApplication.sendEvent(widget, evt)
    widget.update()


def retain_size_when_hidden(widgets):
    for widget in widgets:
        sp = widget.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        widget.setSizePolicy(sp)


class PlayerInfo(QWidget):
    def __init__(self, player_number, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.player_title = QLabel(f"player #{player_number}")

        self.player_name = QLabel("Batman")
        self.player_name.setProperty("player", player_number)  # for stylesheet
        # self.player_name.setProperty("dead", True)

        self.cursors_title = QLabel(f"cursors:")

        self.cursor_number = QLabel("0")

        self.cursor_number.setProperty(
            "player", player_number
        )  # for stylesheet

        self.cursor_number.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Preferred
        )

        retain_size_when_hidden(self)

    def __iter__(self):
        return iter((self.player_title, self.player_name, self.cursors_title, self.cursor_number))

    def set_visible(self, visible: bool):
        for widget in self:
            widget.setVisible(visible)

    def set_name(self, name: str):
        self.player_name.setText(name)

    def set_cursors_count(self, count: int):
        self.cursor_number.setText(str(count))

        if count == 0:
            self.cursor_number.setProperty(
                "lighted", True
            )

            update_stylesheet(self.cursor_number)

    def declare_winner(self):
        self.cursor_number.setText("winner")
        self.cursor_number.setProperty("lighted", True)
        update_stylesheet(self.cursor_number)

    def declare_loser(self):
        self.cursor_number.setText("loser")
        self.cursor_number.setProperty("lighted", True)
        update_stylesheet(self.cursor_number)


class GameInfo(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_finished = False

        self.status = QLabel("paused")
        self.status.setProperty("status", "paused")  # for stylesheet
        self.status.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        self.speed_title = QLabel("speed")
        self.speed_value = QLabel("1")
        self.speed_value.setProperty("lighted", True)  # for stylesheet

        self.cycle_title = QLabel("cycle")
        self.cycle_number = QLabel("0")
        self.cycle_number.setProperty("lighted", True)  # for stylesheet

        retain_size_when_hidden(self)

    def set_paused(self, paused: bool):
        if self.game_finished:
            return

        self.status.setText("paused" if paused else "playing")
        self.status.setProperty(
            "status", "paused" if paused else "play")  # for stylesheet

        update_stylesheet(self.status)

    def set_cycle(self, cycle: int):
        self.cycle_number.setText(str(cycle))

    def set_speed(self, speed: int):
        self.speed_value.setText(str(speed))

    def set_game_finished(self):
        self.game_finished = True
        self.status.setText("finished")
        self.status.setProperty("status", "paused")  # for stylesheet
        update_stylesheet(self.status)

    def __iter__(self):
        return iter((self.status, self.speed_title, self.speed_value, self.cycle_title, self.cycle_number))
