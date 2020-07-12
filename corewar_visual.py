#!/usr/bin/env python3

import sys
from random import random
from functools import partial
from typing import List

from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QTimer

from stdin_listener import StdinListener
from colors import *
from view import View
from corewar_state_manager import CorewarStateManager
from corewar_parser import CorewarParser


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
        "+- to speed up/slow down\n \"D\" next step paused"
    )


def run_or_pause():
    stdin_listener.set_paused(not stdin_listener.paused)
    view.set_paused(stdin_listener.paused)


def read_next_cycle():
    if not stdin_listener.paused:
        stdin_listener.set_paused(True)
        view.set_paused(True)

    stdin_listener.read_next_cycle()


def on_key_pressed(key: str):
    actions = {
        " ": run_or_pause,
        "d": read_next_cycle
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

    stdin_listener.start_paused()
    view.show()

    sys.exit(app.exec_())
