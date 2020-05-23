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
    def __init__(self, addr=0):
        self.i = 0
        self.j = 0
        self.addr = addr

    @property
    def addr(self):
        return self._addr

    @addr.setter
    def addr(self, value):
        self._addr = value % 4096

        self.i = self._addr % 64
        self.j = self._addr // 64

        self.pos = self.i, self.j


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

    def add_carret(self, player_name, carret_name, addr):
        player = self.players[player_name]

        if carret_name in player.carrets:
            raise Exception(carret_name + " carret already exists")

        player.carrets[carret_name] = Carret(addr=addr)

        self.view.update_carrets_layer(self.players)

    def move_carret(self, player_name, carret_name, num_bytes):
        player = self.players[player_name]
        carret = player.carrets[carret_name]

        carret.addr += num_bytes

        self.view.update_carrets_layer(self.players)

    def move_carret_2(self, player_name, carret_name, num_bytes):
        player_this = self.players[player_name]
        carret_this = player_this.carrets[carret_name]

        brush = BRUSH_EMPTY

        # check if any other carrets on the same pos as carret_this
        # if so erase old carret pos with other carret's brush
        for player in self.players.values():
            for carret in player.carrets.values():
                if carret != carret_this:
                    if carret.i == carret_this.i and carret.j == carret_this.j:
                        brush = player.brush
                        break
            else:
                continue
            break

        # erase carret from old pos
        view.draw_carret_rect(carret_this.pos, brush)

        carret_this.addr += num_bytes

        # draw carret at new pos
        view.draw_carret_rect(
            carret_this.pos, player_this.brush, True, carret_this.addr)


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
        self.bytes_pixmap = self.create_pixmap(transparent=True)
        self.bytes_field = self.build_bytes_field()
        self.carrets_pixmap = self.create_pixmap(transparent=False)

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

        # painter.setBrush(BRUSH_EMPTY)
        painter.setBrush(Qt.transparent)

        painter.setCompositionMode(QPainter.CompositionMode_Source)

        for digit1, digit2 in pairs(string):
            i, j = next(index)
            txt = digit1 + digit2

            byte_rect.moveTopLeft(QPoint(i*self.byte_advance, j*h))
            painter.setPen(Qt.NoPen)
            painter.drawRect(byte_rect)

            painter.setPen(pen)
            painter.drawText(byte_rect, Qt.AlignCenter, f'{txt}')

        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

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
        # painter.setCompositionMode(QPainter.CompositionMode_Source)
        # painter.fillRect(self.carrets_pixmap.rect(), Qt.transparent)
        # painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.fillRect(self.carrets_pixmap.rect(), BRUSH_EMPTY)

        carret_rect = QRect(self.byte_rect)
        h = carret_rect.height()

        # painter.setOpacity(0.6)

        painter.setPen(Qt.NoPen)

        for player in players.values():
            brush = player.brush
            painter.setBrush(brush)

            for carret in player.carrets.values():
                addr = carret.addr
                i, j = carret.pos

                #txt = self.bytes_field[addr][0]

                carret_rect.moveTopLeft(QPoint(i*self.byte_advance, j*h))
                painter.drawRect(carret_rect)

                # painter.setPen(PEN_BLACK)
                #painter.drawText(carret_rect, Qt.AlignCenter, f'{txt}')
        # painter.setOpacity(1)

        painter.end()

    def draw_carret_rect(self, pos, brush, draw_byte_value=False, addr=0):
        painter = QPainter(self.carrets_pixmap)

        carret_rect = QRect(self.byte_rect)
        h = carret_rect.height()
        i, j = pos

        carret_rect.moveTopLeft(QPoint(i*self.byte_advance, j*h))

        painter.setPen(Qt.NoPen)
        painter.setBrush(brush)
        painter.drawRect(carret_rect)

        # if draw_byte_value:
        #     painter.setFont(self.font)
        #     txt = self.bytes_field[addr][0]
        #     painter.setPen(PEN_BLACK)
        #     painter.drawText(carret_rect, Qt.AlignCenter, f'{txt}')

        painter.end()

    def paintEvent(self, event):
        painter = QPainter(self)

        # clear background
        painter.setBackground(QCOLOR_BKG_EMPTY)
        painter.eraseRect(self.rect())

        pixmap_pos = self.compute_bytes_pixmap_pos()

        # draw carrets layer
        painter.setOpacity(1)
        painter.drawPixmap(pixmap_pos, self.carrets_pixmap)
        painter.setOpacity(1)

        # draw memory view layer
        painter.drawPixmap(pixmap_pos, self.bytes_pixmap)

    def timerEvent(self, event):
        # render bytes to pixmap
        self.update()


test_curr_addr = 0
timer = QTimer()


def test(view):
    core_manager = CoreManager(view)
    core_manager.add_player("p1")

    core_manager.add_player("p2")

    core_manager.add_player("p3")

    core_manager.add_player("p4")

    for name in core_manager.players:
        for i in range(10):
            core_manager.add_carret(name, f"c{i}", int(random()*4096))

    timer.timeout.connect(functools.partial(test_update, core_manager))
    timer.start(1000/60)


def test_update(core_manager):
    global test_curr_addr

    n = int(random()*256)
    h_value = f'{n:02X}'
    addr = test_curr_addr

    for player in core_manager.players.values():
        player.write_bytes(int(random()*4096), h_value, core_manager.view)

    core_manager.players["p1"].write_bytes(addr, h_value, core_manager.view)

    for player_name, player in core_manager.players.items():
        for carret_name in player.carrets:
            core_manager.move_carret_2(player_name, carret_name, 1)

    test_curr_addr += 1


if __name__ == "__main__":
    app = QApplication()
    view = ByteView()
    view.show()

    test(view)

    sys.exit(app.exec_())
