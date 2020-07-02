from typing import Dict

from colors import *


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
        self.carrets: Dict[str, Carret] = dict()

    def write_bytes(self, addr, bytes_str, view):
        view.write_bytes(addr, bytes_str, self.pen)


class CorewarStateManager:
    """
    represents current state of memory, players and carrets.
    uses view to draw the state
    """

    def __init__(self, view):
        self.view = view
        self.players: Dict[str, Player] = dict()

    def add_player(self, name):
        if name in self.players:
            raise Exception(name + " player already exists")

        self.players[name] = Player(next(next_pen), next(next_brush))

    def add_carret(self, player_name, carret_name, addr):
        player = self.players[player_name]

        if carret_name in player.carrets:
            raise Exception(carret_name + " carret already exists")

        new_carret = Carret(addr=addr)
        player.carrets[carret_name] = new_carret

        self.view.draw_carret_rect(
            new_carret.pos, player.brush, new_carret.addr)

    def kill_carret(self, player_name, carret_name):
        player = self.players[player_name]
        carret = player.carrets[carret_name]

        del player.carrets[carret_name]

        self.view.erase_carret_rect(carret.pos)

    def move_carret(self, player_name, carret_name, num_bytes):
        player_this: Player = self.players[player_name]
        carret_this: Carret = player_this.carrets[carret_name]

        repaint_carret = False

        # check if any other carrets on the same pos as carret_this
        # if so erase old carret pos with other carret's brush
        for player in self.players.values():
            for carret in player.carrets.values():
                if carret != carret_this:
                    if carret.i == carret_this.i and carret.j == carret_this.j:
                        repaint_carret = True
                        brush = player.brush
                        break
            else:
                continue
            break

        # erase carret from old pos
        if repaint_carret:
            self.view.draw_carret_rect(
                carret_this.pos, brush, carret_this.addr)
        else:
            self.view.erase_carret_rect(carret_this.pos)

        carret_this.addr += num_bytes

        # draw carret at new pos
        self.view.draw_carret_rect(
            carret_this.pos, player_this.brush, carret_this.addr)

    def write_bytes(self, player_name, addr, bytes_str):
        player: Player = self.players[player_name]

        player.write_bytes(addr, bytes_str, self.view)
