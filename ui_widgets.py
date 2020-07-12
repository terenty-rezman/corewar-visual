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


class PlayerInfo(QWidget):
    def __init__(self, player_number, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setVerticalSpacing(0)
        self.setLayout(layout)

        layout.addWidget(QLabel(f"player #{player_number}"), 0, 0)

        self.name_widget = QLabel("Batman")
        self.name_widget.setProperty("player", player_number)  # for stylesheet
        self.name_widget.setProperty("dead", True)
        layout.addWidget(self.name_widget, 0, 1)

        layout.addWidget(QLabel(f"cursors:"), 1, 0)

        self.cursor_number = QLabel("0")
        self.cursor_number.setProperty(
            "player", player_number)  # for stylesheet
        self.cursor_number.setProperty(
            "lighted", True)
        self.cursor_number.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Preferred)
        layout.addWidget(self.cursor_number, 1, 1)


class GameInfo(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setVerticalSpacing(10)
        layout.setHorizontalSpacing(2)
        self.setLayout(layout)

        self.status = QLabel("paused")
        self.status.setProperty("status", "paused")  # for stylesheet
        self.status.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        z = self.status.sizeHint().width()
        layout.setColumnMinimumWidth(0, 70)
        layout.addWidget(self.status, 0, 0)

        layout.addWidget(QLabel("speed"), 1, 0)
        self.speed = QLabel("1")
        self.speed.setProperty("lighted", True)  # for stylesheet
        layout.addWidget(self.speed, 1, 1)

        layout.addWidget(QLabel("cycle"), 2, 0)
        self.cycle_number = QLabel("0")
        self.cycle_number.setProperty("lighted", True)  # for stylesheet
        layout.addWidget(self.cycle_number, 2, 1)

    def set_paused(self, paused: bool):
        self.status.setText("paused" if paused else "playing")
        self.status.setProperty(
            "status", "paused" if paused else "play")  # for stylesheet

        update_stylesheet(self.status)

    def set_cycle(self, cycle: int):
        self.cycle_number.setText(str(cycle))

    def set_speed(self, speed: int):
        self.speed.setText(str(speed))
