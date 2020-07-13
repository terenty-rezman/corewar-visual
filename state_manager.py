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
    def __init__(self, number, name, pen, brush):
        self.number = number
        self.name = name
        self.pen = pen
        self.brush = brush
        self.cursors: Dict[str, Carriage] = dict()

    def write_bytes(self, addr, bytes_str, view):
        view.write_bytes(addr, bytes_str, self.pen)


class CorewarStateManager:
    """
    represents current state of memory, players and cursors.
    uses view to draw the state
    """

    def __init__(self, view):
        self.view = view
        self.players: Dict[str, Player] = dict()

    def add_player(self, id, name):
        if name in self.players:
            raise Exception(name + " player already exists")

        player_number = len(self.players)

        self.players[id] = Player(
            player_number, name, next(next_pen), next(next_brush)
        )

        self.view.add_player(name[:8])

    def add_cursor(self, player_id, carriage_id, addr):
        player: Player = self.players[player_id]

        if carriage_id in player.cursors:
            raise Exception(carriage_id + " carriage already exists")

        new_cursor = Carriage(addr=addr)
        player.cursors[carriage_id] = new_cursor

        self.view.draw_cursor_rect(
            new_cursor.pos, player.brush, new_cursor.addr)

        self.view.set_cursor_count(player.number, len(player.cursors))

    def kill_cursor(self, player_id, carriage_id):
        player: Player = self.players[player_id]
        cursor = player.cursors[carriage_id]

        del player.cursors[carriage_id]

        self.view.erase_cursor_rect(cursor.pos)

        self.view.set_cursor_count(player.number, len(player.cursors))

    def move_cursor(self, player_id, carriage_id, num_bytes):
        player_this: Player = self.players[player_id]
        cursor_this: Carriage = player_this.cursors[carriage_id]

        repaint_cursor = False

        # check if any other cursors on the same pos as cursor_this
        # if so erase old cursor pos with other cursor's brush
        for player in self.players.values():
            for cursor in player.cursors.values():
                if cursor != cursor_this:
                    if cursor.i == cursor_this.i and cursor.j == cursor_this.j:
                        repaint_cursor = True
                        brush = player.brush
                        break
            else:
                continue
            break

        # erase cursor from old pos
        if repaint_cursor:
            self.view.draw_cursor_rect(
                cursor_this.pos, brush, cursor_this.addr)
        else:
            self.view.erase_cursor_rect(cursor_this.pos)

        cursor_this.addr += num_bytes

        # draw cursor at new pos
        self.view.draw_cursor_rect(
            cursor_this.pos, player_this.brush, cursor_this.addr)

    def write_bytes(self, player_id, addr, bytes_str):
        player: Player = self.players[player_id]

        player.write_bytes(addr, bytes_str, self.view)

    def declare_winner(self, player_id):
        player: Player = self.players[player_id]
        self.view.declare_winner(player.number)
