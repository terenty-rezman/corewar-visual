import sys
from random import random
from itertools import repeat

from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QTransform, QPixmap
from PySide2.QtCore import QObject, QRect, QRectF, QPoint, QPointF, Slot, Signal, Qt


def pairs(string):
    it = iter(string)
    try:
        while True:
            a = next(it)
            b = next(it)
            yield a, b
    except StopIteration:
        pass


colors = ["#D34C75", "#E9C13B", "#0A92AC", "#8662EA"]
pens = [QPen(QColor(color)) for color in colors]

COLOR_EMPTY = "#4D4D4D"
QCOLOR_EMPTY = QColor(COLOR_EMPTY)
PEN_EMPTY = QPen(QCOLOR_EMPTY)

COLOR_BKG_EMPTY = "#1D1D1D"
QCOLOR_BKG_EMPTY = QColor(COLOR_BKG_EMPTY)
BRUSH_EMPTY = QBrush(QCOLOR_BKG_EMPTY)


class Carret:
    def __init__(self, addr=0, brush=QBrush(COLOR_EMPTY)):
        self.addr = addr
        self.brush = brush

    @property
    def addr(self):
        return self._addr

    @addr.setter
    def addr(self, value):
        self._addr = value % 4096

        i = self._addr % 64
        j = self._addr // 64

        self.pos = i, j


class ByteView(QWidget):
    initialized = False
    byte_margin = 5
    byte_padding = 2

    test_curr_addr = 0

    def __init__(self, parent=None):
        super().__init__(parent)

        self.startTimer(1000/60)

    def initialize(self, painter):
        font = QApplication.font()
        font.setPixelSize(14)
        # font.setBold(True)
        self.font = font

        painter.setFont(self.font)

        self.byte_rect = self.compute_byte_rect(painter)
        self.byte_advance = self.compute_byte_advance(painter)
        self.bytes_pixmap = self.build_bytes_pixmap()
        self.bytes_field = self.build_bytes_field()

    def compute_byte_rect(self, painter):
        fm = painter.fontMetrics()
        byte_rect = fm.boundingRect("00")
        byte_rect.moveTopLeft(QPoint())

        return byte_rect.adjusted(-self.byte_padding, 0, self.byte_padding, 0)

    def compute_byte_advance(self, painter):
        fm = painter.fontMetrics()
        return fm.horizontalAdvance("00") + 2*self.byte_padding + self.byte_margin

    def build_bytes_pixmap(self):
        w = self.byte_advance * 64
        h = self.byte_rect.height() * 64

        return QPixmap(w, h)

    def build_bytes_field(self):
        l = []
        for _ in range(4096):
            l.append(["00", PEN_EMPTY])

        return l

    def compute_bytes_pixmap_pos(self):
        view_width = self.rect().width()
        view_height = self.rect().height()
        pixmap_width = self.bytes_pixmap.width()
        pixmap_height = self.bytes_pixmap.height()

        h_margin = None
        v_margin = None

        if view_width > pixmap_width:
            h_margin = (view_width - pixmap_width) / 2

        if view_height > pixmap_height:
            v_margin = (view_height - pixmap_height) / 2

        return QPoint(h_margin or 0, v_margin or 0)

    def render_empty_bytes_to_pixmap(self):
        pixmap_painter = QPainter(self.bytes_pixmap)
        pixmap_painter.setFont(self.font)
        self.draw_empty_bytes(pixmap_painter)
        pixmap_painter.end()

    def draw_empty_bytes(self, painter):
        byte_rect = QRect(self.byte_rect)
        h = byte_rect.height()

        # clear pixmap
        painter.setBackground(QCOLOR_BKG_EMPTY)
        painter.eraseRect(self.bytes_pixmap.rect())

        # fill with empty values
        painter.setPen(PEN_EMPTY)

        for i in range(64):
            for j in range(64):
                byte_rect.moveTopLeft(QPoint(i*self.byte_advance, j*h))
                painter.drawText(byte_rect, Qt.AlignCenter, '00')

    def byte_index(self, byte_addr):
        while True:
            looped_addr = byte_addr % 4096
            i = looped_addr % 64
            j = looped_addr // 64
            yield i, j
            byte_addr += 1

    def update_pixmap(self):
        pixmap_painter = QPainter(self.bytes_pixmap)
        pixmap_painter.setFont(self.font)

        n = int(random()*256)
        h_value = f'{n:02X}'
        pen = QPen(QColor("#000"))
        pens[int(random()*4)]
        addr = self.test_curr_addr
        self.test_curr_addr += 1

        self.print_to_pixmap(pixmap_painter, addr, h_value, pen)

        self.print_to_bytes_field(addr, h_value, pen)

        pixmap_painter.end()

    def print_to_pixmap(self, painter, byte_addr, string, pen):
        index = self.byte_index(byte_addr)
        byte_rect = QRect(self.byte_rect)
        h = byte_rect.height()

        painter.setBrush(QBrush(QColor(colors[int(random()*4)])))

        for digit1, digit2 in pairs(string):
            i, j = next(index)
            txt = digit1 + digit2

            byte_rect.moveTopLeft(QPoint(i*self.byte_advance, j*h))
            painter.setPen(Qt.NoPen)
            painter.drawRect(byte_rect)

            painter.setPen(pen)
            painter.drawText(byte_rect, Qt.AlignCenter, f'{txt}')

    def print_to_bytes_field(self, byte_addr, string, pen):
        for digit1, digit2 in pairs(string):
            looped_addr = byte_addr % 4096
            txt = digit1 + digit2
            cell = self.bytes_field[looped_addr]
            cell[0] = txt
            cell[1] = pen
            byte_addr += 1

    def paintEvent(self, event):
        painter = QPainter(self)

        if not self.initialized:
            self.initialize(painter)
            self.render_empty_bytes_to_pixmap()
            self.initialized = True

        # clear background
        painter.setBackground(QCOLOR_BKG_EMPTY)
        painter.eraseRect(self.rect())

        pixmap_pos = self.compute_bytes_pixmap_pos()
        painter.drawPixmap(pixmap_pos, self.bytes_pixmap)

    def timerEvent(self, event):
        if not self.initialized:
            return

        # render bytes to pixmap
        self.update_pixmap()
        self.update()


if __name__ == "__main__":
    app = QApplication()
    view = ByteView()
    view.show()
    sys.exit(app.exec_())
