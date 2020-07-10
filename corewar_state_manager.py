from typing import Dict

from colors import *


class Carriage:
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
    def __init__(self, name, pen, brush):
        self.name = name
        self.pen = pen
        self.brush = brush
        self.carrets: Dict[str, Carriage] = dict()

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

    def add_player(self, id, name):
        if name in self.players:
            raise Exception(name + " player already exists")

        self.players[id] = Player(name, next(next_pen), next(next_brush))

    def add_carret(self, player_id, carriage_id, addr):
        player = self.players[player_id]

        if carriage_id in player.carrets:
            raise Exception(carriage_id + " carret already exists")

        new_carret = Carriage(addr=addr)
        player.carrets[carriage_id] = new_carret

        self.view.draw_carret_rect(
            new_carret.pos, player.brush, new_carret.addr)

    def kill_carret(self, player_id, carriage_id):
        player = self.players[player_id]
        carret = player.carrets[carriage_id]

        del player.carrets[carriage_id]

        self.view.erase_carret_rect(carret.pos)

    def move_carret(self, player_id, carriage_id, num_bytes):
        player_this: Player = self.players[player_id]
        carret_this: Carriage = player_this.carrets[carriage_id]

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

    def write_bytes(self, player_id, addr, bytes_str):
        player: Player = self.players[player_id]

        player.write_bytes(addr, bytes_str, self.view)
