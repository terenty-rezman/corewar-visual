#!/usr/bin/env python3

import sys
from random import random
import functools

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

if __name__ == "__main__":
    app = QApplication()

    view = View()
    manager = CorewarStateManager(view.byte_view)
    parser = CorewarParser(manager)
    stdin_listener = StdinListener(parser.parser_corewar_output, 500)

    stdin_listener.start()
    view.show()

    sys.exit(app.exec_())
