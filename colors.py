import itertools

from PySide2.QtGui import QPen, QBrush, QColor

colors = ["#D34C75", "#E9C13B", "#0A92AC", "#8662EA"]
pens = [QPen(QColor(color)) for color in colors]
brushes = [QBrush(QColor(color)) for color in colors]

COLOR_BKG_EMPTY = "#1D1D1D"
QCOLOR_BKG_EMPTY = QColor(COLOR_BKG_EMPTY)
BRUSH_EMPTY = QBrush(QCOLOR_BKG_EMPTY)

COLOR_EMPTY = "#4D4D4D"
QCOLOR_EMPTY = QColor(COLOR_EMPTY)
PEN_EMPTY = QPen(QCOLOR_EMPTY)
PEN_BLACK = QPen(QColor("#000"))
PEN_BCK = QPen("#2D2D2D")
PEN_LIGHT = QPen("#8A9199")
PEN_WARNING = QPen("#C3486B")

next_pen = itertools.cycle(pens)
next_brush = itertools.cycle(brushes)
