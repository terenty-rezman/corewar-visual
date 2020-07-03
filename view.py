from typing import List, Dict, Tuple

from PySide2.QtWidgets import QApplication, QWidget, QScrollArea, QHBoxLayout, QSizePolicy
from PySide2.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QTransform, QPixmap, QFontMetrics
from PySide2.QtCore import QObject, QRect, QRectF, QPoint, QPointF, Slot, Signal, Qt, QTimer

from colors import *


def pairs(string):
    it = iter(string)
    try:
        while True:
            a = next(it)
            b = next(it)
            yield a, b
    except StopIteration:
        pass


class View(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.byte_view = ByteView()
        self.scroll_area = QScrollArea()
        self.layout = QHBoxLayout()

        self.scroll_area.setWidget(self.byte_view)
        self.scroll_area.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)

        self.style()

    def style(self):
        self.layout.setContentsMargins(0, 0, 0, 0)
        # make scrollbars above content
        self.scroll_area.setViewportMargins(0, 0, -8, -8)

        with open("stylesheet.qss") as file:
            stylesheet = file.read()

        self.setStyleSheet(stylesheet)


class ByteView(QWidget):
    """
    Is used to draw memory, players and carrets state onto a widget
    """
    byte_margin = 0
    byte_padding = 4

    test_curr_addr = 0

    def __init__(self, parent=None):
        super().__init__(parent)

        self.initialize()
        self.startTimer(1000/60)

    def initialize(self):
        font = QApplication.font()
        font.setPixelSize(14)
        # font.setBold(True)
        self.font = font

        self.byte_rect = self.compute_byte_rect()
        self.byte_advance = self.compute_byte_advance()
        self.bytes_pixmap = self.create_pixmap(transparent=False)
        self.bytes_field = self.build_bytes_field()
        self.carrets_pixmap = self.create_pixmap(transparent=True)

        self.setMinimumWidth(self.bytes_pixmap.width())
        self.setMinimumHeight(self.bytes_pixmap.height())

        self.render_empty_bytes_to_pixmap()

    def compute_byte_rect(self):
        fm = QFontMetrics(self.font)
        byte_rect = fm.boundingRect("00")
        byte_rect.moveTopLeft(QPoint())

        return byte_rect.adjusted(-self.byte_padding, 0, self.byte_padding, 0)

    def compute_byte_advance(self):
        fm = QFontMetrics(self.font)
        # return fm.horizontalAdvance("00") + 2*self.byte_padding + self.byte_margin
        return fm.boundingRect("00").width() + 2*self.byte_padding + self.byte_margin

    def create_pixmap(self, transparent=False):
        w = self.byte_advance * 64
        h = self.byte_rect.height() * 64

        pixmap = QPixmap(w, h)

        if transparent:
            pixmap.fill(Qt.transparent)

        return pixmap

    def build_bytes_field(self):
        l = []
        for _ in range(4096):
            l.append(["00", PEN_EMPTY])

        return l

    def render_empty_bytes_to_pixmap(self):
        pixmap_painter = QPainter(self.bytes_pixmap)
        pixmap_painter.setFont(self.font)

        self.print_to_pixmap(pixmap_painter, 0, "00"*4096, PEN_EMPTY)

        pixmap_painter.end()

    def byte_index(self, byte_addr):
        while True:
            looped_addr = byte_addr % 4096
            i = looped_addr % 64
            j = looped_addr // 64
            yield i, j
            byte_addr += 1

    def write_bytes(self, addr, bytes_str, pen):
        pixmap_painter = QPainter(self.bytes_pixmap)
        pixmap_painter.setFont(self.font)

        self.print_to_pixmap(pixmap_painter, addr, bytes_str, pen)
        pixmap_painter.end()

        self.print_to_bytes_field(addr, bytes_str, pen)

    def print_to_pixmap(self, painter, byte_addr, string, pen):
        index = self.byte_index(byte_addr)
        byte_rect = QRect(self.byte_rect)
        h = byte_rect.height()

        painter.setBrush(BRUSH_EMPTY)

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

    def draw_carret_rect(self, pos: Tuple[int, int], brush, addr):
        painter = QPainter(self.carrets_pixmap)

        carret_rect = QRect(self.byte_rect)
        h = carret_rect.height()
        i, j = pos

        carret_rect.moveTopLeft(QPoint(i*self.byte_advance, j*h))

        painter.setPen(Qt.NoPen)
        painter.setBrush(brush)
        painter.drawRect(carret_rect)

        painter.setFont(self.font)
        txt = self.bytes_field[addr][0]
        painter.setPen(PEN_BCK)
        painter.drawText(carret_rect, Qt.AlignCenter, f'{txt}')

        painter.end()

    def erase_carret_rect(self, pos: Tuple[int, int]):
        painter = QPainter(self.carrets_pixmap)

        carret_rect = QRect(self.byte_rect)
        h = carret_rect.height()
        i, j = pos

        carret_rect.moveTopLeft(QPoint(i*self.byte_advance, j*h))

        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.transparent)
        painter.drawRect(carret_rect)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

    def paintEvent(self, event):
        painter = QPainter(self)

        # clear background
        painter.setBackground(QCOLOR_BKG_EMPTY)
        painter.eraseRect(self.rect())

        # draw memory view layer
        painter.drawPixmap(QPoint(), self.bytes_pixmap)

        # draw carrets layer
        painter.drawPixmap(QPoint(), self.carrets_pixmap)

    def timerEvent(self, event):
        # render bytes to pixmap
        self.update()
