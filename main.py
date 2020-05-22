import sys
from random import random
import itertools
import functools

from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QTransform, QPixmap, QFontMetrics
from PySide2.QtCore import QObject, QRect, QRectF, QPoint, QPointF, Slot, Signal, Qt, QTimer


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
brushes = [QBrush(QColor(color)) for color in colors]

COLOR_EMPTY = "#4D4D4D"
QCOLOR_EMPTY = QColor(COLOR_EMPTY)
PEN_EMPTY = QPen(QCOLOR_EMPTY)
PEN_BLACK = QPen(QColor("#000"))

COLOR_BKG_EMPTY = "#1D1D1D"
QCOLOR_BKG_EMPTY = QColor(COLOR_BKG_EMPTY)
BRUSH_EMPTY = QBrush(QCOLOR_BKG_EMPTY)

next_pen = itertools.cycle(pens)
next_brush = itertools.cycle(brushes)


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


class Player:
    def __init__(self, pen, brush):
        self.pen = pen
        self.brush = brush
        self.carrets = dict()

    def write_bytes(self, addr, bytes_str, view):
        view.write_bytes(addr, bytes_str, self.pen)


class CoreManager:
    def __init__(self, view):
        self.view = view
        self.players = dict()

    def add_player(self, name):
        if name in self.players:
            raise Exception(name + " player already exists")

        self.players[name] = Player(next(next_pen), next(next_brush))

    def add_carret(self, player_name, carret_name):
        player = self.players[player_name]

        if carret_name in player.carrets:
            raise Exception(carret_name + " carret already exists")

        player.carrets[carret_name] = Carret(
            brush=player.brush, addr=int(random()*55))

        self.view.update_carrets_layer(self.players)


class ByteView(QWidget):
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
        self.bytes_pixmap = self.create_pixmap()
        self.bytes_field = self.build_bytes_field()
        self.carrets_pixmap = self.create_pixmap(transparent=True)

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

    def update_carrets_layer(self, players):
        painter = QPainter(self.carrets_pixmap)
        painter.setFont(self.font)

        # clear background
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(self.carrets_pixmap.rect(), Qt.transparent)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        carret_rect = QRect(self.byte_rect)
        h = carret_rect.height()

        painter.setOpacity(0.5)

        for player in players.values():
            for carret in player.carrets.values():
                addr = carret.addr
                i, j = carret.pos
                brush = carret.brush

                txt = self.bytes_field[addr][0]

                carret_rect.moveTopLeft(QPoint(i*self.byte_advance, j*h))

                painter.setPen(Qt.NoPen)
                painter.setBrush(brush)
                painter.drawRect(carret_rect)

                # painter.setPen(PEN_BLACK)
                #painter.drawText(carret_rect, Qt.AlignCenter, f'{txt}')
        painter.setOpacity(1)

        painter.end()

    def paintEvent(self, event):
        painter = QPainter(self)

        # clear background
        painter.setBackground(QCOLOR_BKG_EMPTY)
        painter.eraseRect(self.rect())

        pixmap_pos = self.compute_bytes_pixmap_pos()

        # draw memory view layer
        painter.drawPixmap(pixmap_pos, self.bytes_pixmap)
        # draw carrets layer
        painter.drawPixmap(pixmap_pos, self.carrets_pixmap)

    def timerEvent(self, event):
        # render bytes to pixmap
        self.update()


test_curr_addr = 0
timer = QTimer()


def test(view):
    core_manager = CoreManager(view)
    core_manager.add_player("p1")
    core_manager.add_carret("p1", "c1")

    core_manager.add_player("p2")
    core_manager.add_carret("p2", "c2")

    core_manager.add_player("p3")
    core_manager.add_carret("p3", "c3")

    core_manager.add_player("p4")
    core_manager.add_carret("p4", "c4")

    timer.timeout.connect(functools.partial(test_update, core_manager))
    timer.start(1000 / 60)


def test_update(core_manager):
    global test_curr_addr

    n = int(random()*256)
    h_value = f'{n:02X}'
    addr = test_curr_addr

    core_manager.players["p1"].write_bytes(addr, h_value, core_manager.view)

    core_manager.players["p2"].write_bytes(
        int(random()*4096), h_value, core_manager.view)

    core_manager.players["p3"].write_bytes(
        int(random()*4096), h_value, core_manager.view)

    core_manager.players["p4"].write_bytes(
        int(random()*4096), h_value, core_manager.view)

    test_curr_addr += 1


if __name__ == "__main__":
    app = QApplication()
    view = ByteView()
    view.show()

    test(view)

    sys.exit(app.exec_())
