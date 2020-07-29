#!/usr/bin/env python3

import sys
from random import random
from functools import partial
from typing import List

from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QTimer

from cw_visual.stdin_listener import StdinListener
from cw_visual.colors import PEN_WARNING
from cw_visual.view import View
from cw_visual.state_manager import CorewarStateManager
from cw_visual.cw_parser import CorewarParser


def uncaught_exception_hook(exctype, value, tb):
    if exctype == KeyboardInterrupt:
        sys.exit(0)
    else:
        raise value


# catch KeyboardInterrupt event on top level
sys.excepthook = uncaught_exception_hook


def print_no_stdin_data_msg():
    view.print_msg(
        "corewar 42\n\nno input on stdin",
        {2: PEN_WARNING}
    )


def print_controls_info_msg():
    view.print_msg(
        "corewar 42\n\npress \"space\" to run/pause the simulation\n"
        "+-to speed up/slow down\n\"D\" next step paused\n"
        "Alt + enter to go fullscreen\n"
        " F11 to go fullscreen"
    )


def run_or_pause():
    stdin_listener.set_paused(not stdin_listener.paused)
    view.set_paused(stdin_listener.paused)


def read_next_cycle():
    if not stdin_listener.paused:
        stdin_listener.set_paused(True)
        view.set_paused(True)

    stdin_listener.read_next_cycle()


def set_play_speed(speed: int):
    stdin_listener.set_speed(speed)
    view.set_speed(stdin_listener.speed + 1)


def speed_up():
    stdin_listener.speed_up()
    view.set_speed(stdin_listener.speed + 1)


def slow_down():
    stdin_listener.slow_down()
    view.set_speed(stdin_listener.speed + 1)


def on_key_pressed(key: str):
    actions = {
        " ": run_or_pause,
        "d": read_next_cycle,
        "+": speed_up,
        "-": slow_down
    }

    action = actions.get(key, lambda: None)
    action()


def on_stdin_data(cycle: int, data: str or List[str]):
    view.set_cycle(cycle)

    if isinstance(data, str) and data == "start":
        print_controls_info_msg()
    else:
        parser.parse_corewar_output(data)


if __name__ == "__main__":
    app = QApplication()

    view = View()

    view.key_pressed.connect(on_key_pressed)

    manager = CorewarStateManager(view)
    parser = CorewarParser(manager)
    stdin_listener = StdinListener(on_stdin_data, 100)

    print_no_stdin_data_msg()

    set_play_speed(3)

    stdin_listener.start_paused()
    view.show()

    sys.exit(app.exec_())
