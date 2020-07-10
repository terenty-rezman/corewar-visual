#!/usr/bin/env python3

import time
import sys
import functools

# this script emulates output of corewar vm to stdout
# used to test corewar_visual in abscence of corewar vm

sep = '"'  # separator sign


def add_player(cycle, player_id, name, address, bytes):
    print(
        f'p{sep}{cycle}{sep}{player_id}{sep}{name}{sep}{address}{sep}{bytes}'
    )


def add_carret(cycle, player_id, carret_id, address):
    print(
        f'c{sep}{cycle}{sep}{player_id}{sep}{carret_id}{sep}{address}'
    )


def kill_carret(cycle, player_id, carret_id):
    print(
        f'k{sep}{cycle}{sep}{player_id}{sep}{carret_id}'
    )


def move_carret(cycle, player_id, carret_id, offset):
    print(
        f'm{sep}{cycle}{sep}{player_id}{sep}{carret_id}{sep}{offset}'
    )


def write_memory(cycle, player_id, address, bytes):
    """ st & sti instruction"""
    print(
        f'w{sep}{cycle}{sep}{player_id}{sep}{address}{sep}{bytes}'
    )


sleep = functools.partial(time.sleep, 2)

# start emulating output of corewar vm to stdout
add_player(1, 1, 'Batman', 0, "00002901DA04446963742901DA")
add_player(1, 2, 'Robin', 64*10, "df01bb09")
add_player(1, 3, 'Yoshi', 64*20, "47823958")
add_player(1, 4, 'Mario', 64*50, "44ff55eeaabbcacd9933")

add_carret(2, 1, 1, 0)  # player 1 adds carret 1
add_carret(2, 2, 2, 64*10)  # player 2 adds carret 1
add_carret(2, 3, 3, 64*20)  # player 3 adds carret 1
add_carret(2, 4, 4, 64*50)  # player 4 adds carret 1

add_carret(10, 1, 2, 64*13)  # player 1 adds carret 2

move_carret(20, 1, 2, 4)  # move carret 2 of player 1
move_carret(40, 1, 2, 4)  # move carret 2 of player 1

kill_carret(50, 1, 2)  # kill carret 2 of player 1
