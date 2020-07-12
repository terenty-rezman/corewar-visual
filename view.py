from typing import List, Dict, Tuple
from dataclasses import dataclass

from PySide2.QtWidgets import QApplication, QWidget, QScrollArea, QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollBar, QLabel
from PySide2.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QTransform, QPixmap, QFontMetrics, QFont
from PySide2.QtCore import QObject, QRect, QRectF, QPoint, QPointF, Slot, Signal, Qt, QTimer, QSize

from colors import *
from ui_widgets import *


def pairs(string):
    it = iter(string)
    try:
        while True:
            a = next(it)
            b = next(it)
            yield a, b
    except StopIteration:
        pass


class MouseScrolledArea(QScrollArea):
    """scroll area that can be scrolled with mouse drag"""

    def mousePressEvent(self, ev):
        self.mouse_last_pos = ev.pos()

    def mouseMoveEvent(self, ev):  # mouse move only triggered when a mouse button pressed
        dmouse = ev.pos() - self.mouse_last_pos
        self.scrollContent(-dmouse.x(), -dmouse.y())
        self.mouse_last_pos = ev.pos()

    def scrollContent(self, dx, dy):
        horizontal = self.horizontalScrollBar()
        vertical = self.verticalScrollBar()

        v_value = vertical.value()
        h_value = horizontal.value()

        horizontal.setValue(h_value + dx)
        vertical.setValue(v_value + dy)


class NotifyScrollbar(QScrollBar):
    """scrollbar that notifies when hidden or shown """

    shown = Signal(bool)

    def showEvent(self, event):
        self.shown.emit(True)

    def hideEvent(self, event):
        self.shown.emit(False)


class ScrollsOverContentArea(MouseScrolledArea):
    """ makes scrollbars shown above content
        only to improve ui design
    """
    scrollsWidth = 8  # should follow up with your design

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setVerticalScrollBar(NotifyScrollbar())
        self.setHorizontalScrollBar(NotifyScrollbar())

        self.verticalScrollBar().shown.connect(self.vertical_scrollbar_shown)
        self.horizontalScrollBar().shown.connect(self.horizontal_scrollbar_shown)

    def vertical_scrollbar_shown(self, shown):
        m = self.viewportMargins()
        l = m.left()
        t = m.top()
        b = m.bottom()

        if shown:
            # make scrollbars above content
            self.setViewportMargins(l, t, -self.scrollsWidth, b)
        else:
            # restore vieport margins
            self.setViewportMargins(l, t, 0, b)

    def horizontal_scrollbar_shown(self, shown):
        m = self.viewportMargins()
        l = m.left()
        t = m.top()
        r = m.right()

        if shown:
            # make scrollbars above content
            self.setViewportMargins(l, t, r, -self.scrollsWidth)
        else:
            # restore vieport margins
            self.setViewportMargins(l, t, r, 0)

    def sizeHint(self):
        """use size hint of the child widget"""
        return self.widget().sizeHint()

    def center_view(self):
        vertical = self.verticalScrollBar()
        horizontal = self.horizontalScrollBar()

        ScrollsOverContentArea.center_scrollbar(horizontal)
        ScrollsOverContentArea.center_scrollbar(vertical)

    @staticmethod
    def center_scrollbar(scrollbar: QScrollBar):
        min = scrollbar.minimum()
        max = scrollbar.maximum()

        scrollbar.setValue((max - min) // 4)


class View(QWidget):
    key_pressed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("corewar visual")

        self.byte_view = ByteView()

        self.scroll_area = ScrollsOverContentArea()
        self.scroll_area.setWidget(self.byte_view)

        self.layout = QHBoxLayout()
        self.layout.addStretch()  # add left stretch to main layout to center all content
        self.layout.addWidget(self.scroll_area)

        self.add_ui()
        self.layout.addStretch()  # add right stretch to main layout to center all content

        self.setLayout(self.layout)

        self.style()

        self.scroll_area.center_view()

        # make references to byte_view functions availible on self
        self.draw_cursor_rect = self.byte_view.draw_cursor_rect
        self.erase_cursor_rect = self.byte_view.erase_cursor_rect
        self.write_bytes = self.byte_view.write_bytes
        self.print_msg = self.byte_view.print_msg
        self.set_paused = self.game_info.set_paused

    def add_ui(self):
        v_layout = QVBoxLayout()
        v_layout.setSpacing(20)
        v_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.game_info = GameInfo()
        v_layout.addWidget(self.game_info)

        v_layout.addWidget(PlayerInfo(1))
        v_layout.addWidget(PlayerInfo(2))
        v_layout.addWidget(PlayerInfo(3))
        v_layout.addWidget(PlayerInfo(4))

        v_layout.setContentsMargins(20, 20, 20, 20)
        self.layout.addLayout(v_layout)

    def style(self):
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.scroll_area.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        with open("stylesheet.qss") as file:
            stylesheet = file.read()

        self.setObjectName("main")  # for proper styling
        self.setStyleSheet(stylesheet)

    def keyPressEvent(self, ev):
        if ev.key() == Qt.Key_Space:
            self.key_pressed.emit(" ")
        elif ev.key() == Qt.Key_D:
            self.key_pressed.emit("d")
        elif ev.key() == Qt.Key_Plus:
            self.key_pressed.emit("+")
        elif ev.key() == Qt.Key_Minus:
            self.key_pressed.emit("-")


@dataclass
class MsgLines:
    """
    is used to remember lines occupied by msgs printed to byteview
    in oreder to clear them when new one is going to be printed
    """
    start_line: int
    line_count: int


class ByteView(QWidget):
    """
    Is used to draw memory, players and cursors state onto a widget
    """
    byte_margin = 0
    byte_padding = 4

    test_curr_addr = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize()
        self.startTimer(1000/60)

    def initialize(self):
        font = QApplication.font()
        font.setPixelSize(14)
        # font.setBold(True)
        self.font = font

        self.font_bold = QFont(font)
        self.font_bold.setBold(True)

        self.byte_rect = self.compute_byte_rect()
        self.byte_advance = self.compute_byte_advance()
        self.bytes_pixmap = self.create_pixmap(transparent=False)
        self.bytes_field = self.build_bytes_field()
        self.cursors_pixmap = self.create_pixmap(transparent=True)

        self.setMinimumWidth(self.bytes_pixmap.width())
        self.setMinimumHeight(self.bytes_pixmap.height())

        self.render_empty_bytes_to_pixmap()

        self.prev_msg_lines = MsgLines(0, 0)

    def sizeHint(self):
        return QSize(self.bytes_pixmap.width(), self.bytes_pixmap.height())

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

    def render_empty_bytes_to_pixmap(self, address=0, count=4096):
        pixmap_painter = QPainter(self.bytes_pixmap)
        pixmap_painter.setFont(self.font)

        self.print_to_pixmap(pixmap_painter, address, "00"*count, PEN_EMPTY)

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

    def print_to_bytes_field(self, byte_addr, bytes_str, pen):
        for digit1, digit2 in pairs(bytes_str):
            looped_addr = byte_addr % 4096
            txt = digit1 + digit2
            cell = self.bytes_field[looped_addr]
            cell[0] = txt
            cell[1] = pen
            byte_addr += 1

    def clear_last_msg(self):
        # clear prev msg
        prev_msg_start = self.prev_msg_lines.start_line * 64
        prev_msg_bytes_count = self.prev_msg_lines.line_count * 64

        self.render_empty_bytes_to_pixmap(prev_msg_start, prev_msg_bytes_count)

    def print_msg(self, multiline_msg: str, pens_dict={}):
        """
        prints msg to byte cells vertically and horizontally centered
        pens_dict specifies PEN to be used for specified line 
        eg {0: PEN_WARNING} - line 0 will be painted with PEN_WARNING pen
        """
        self.clear_last_msg()

        pixmap_painter = QPainter(self.bytes_pixmap)
        pixmap_painter.setFont(self.font_bold)

        lines = multiline_msg.splitlines()
        row = 64 // 2 - len(lines) // 2  # centered vertically

        # for clearing this msg when new one printed
        self.prev_msg_lines = MsgLines(row, len(lines))

        for index, line in enumerate(lines):
            line = line.upper()
            line = line.replace(' ', '_')
            if len(line) % 2:  # odd
                line += '_'

            column = 64 // 2 - len(line) // 2 // 2  # centered horizontally
            address = row * 64 + column

            pen = pens_dict.get(index, PEN_LIGHT)
            self.print_to_pixmap(pixmap_painter, address, line, pen)
            row += 1

    def draw_cursor_rect(self, pos: Tuple[int, int], brush, addr):
        painter = QPainter(self.cursors_pixmap)

        cursor_rect = QRect(self.byte_rect)
        h = cursor_rect.height()
        i, j = pos

        cursor_rect.moveTopLeft(QPoint(i*self.byte_advance, j*h))

        painter.setPen(Qt.NoPen)
        painter.setBrush(brush)
        painter.drawRect(cursor_rect)

        painter.setFont(self.font)
        txt = self.bytes_field[addr][0]
        painter.setPen(PEN_BCK)
        painter.drawText(cursor_rect, Qt.AlignCenter, f'{txt}')

        painter.end()

    def erase_cursor_rect(self, pos: Tuple[int, int]):
        painter = QPainter(self.cursors_pixmap)

        cursor_rect = QRect(self.byte_rect)
        h = cursor_rect.height()
        i, j = pos

        cursor_rect.moveTopLeft(QPoint(i*self.byte_advance, j*h))

        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.transparent)
        painter.drawRect(cursor_rect)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

    def paintEvent(self, event):
        painter = QPainter(self)

        # clear background
        painter.setBackground(QCOLOR_BKG_EMPTY)
        painter.eraseRect(self.rect())

        # draw memory view layer
        painter.drawPixmap(QPoint(), self.bytes_pixmap)

        # draw cursors layer
        painter.drawPixmap(QPoint(), self.cursors_pixmap)

    def timerEvent(self, event):
        # render pixmaps to widget
        self.update()
