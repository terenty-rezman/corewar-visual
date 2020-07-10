#!/usr/bin/env python3

import time
import sys
import functools

# this script emulates output of corewar vm to stdout
# used to test corewar_visual in abscence of corewar vm

sep = '"'  # separator sign


def add_player(cycle, player_id, name, address, bytes):
    print(
        f'p{sep}{cycle}{sep}{player_id}{sep}{name}{sep}{address}{sep}{bytes}\n'
    )


def add_carret(cycle, player_id, carret_id, address):
    print(
        f'c{sep}{cycle}{sep}{player_id}{sep}{carret_id}{sep}{address}\n'
    )


def kill_carret(cycle, player_id, carret_id):
    print(
        f'k{sep}{cycle}{sep}{player_id}{sep}{carret_id}\n'
    )


def move_carret(cycle, player_id, carret_id, offset):
    print(
        f'm{sep}{cycle}{sep}{player_id}{sep}{carret_id}{sep}{offset}\n'
    )


sleep = functools.partial(time.sleep, 2)

# start emulating output of corewar vm to stdout
add_player(1, hex(0x000001), 'Batman', 0, "00002901DA04446963742901DA")
add_player(1, 0x000002, 'Robin', 64*10, "df01bb09")
add_player(1, 0x000003, 'Yoshi', 64*20, "47823958")
add_player(1, 0x000004, 'Mario', 64*50, "44ff55eeaabbcacd9933")

sleep()
add_carret(2, 0x000001, 0x000001, 0)  # player 1 adds carret 1
add_carret(2, 0x000002, 0x000002, 64*10)  # player 2 adds carret 1
add_carret(2, 0x000003, 0x000003, 64*20)  # player 3 adds carret 1
add_carret(2, 0x000004, 0x000004, 64*50)  # player 4 adds carret 1

sleep()
add_carret(10, 0x000001, 0x000002, 64*13)  # player 1 adds carret 2
sleep()
move_carret(20, 0x000001, 0x000002, 4)  # move carret 2 of player 1
move_carret(40, 0x000001, 0x000002, 4)  # move carret 2 of player 1
sleep()
kill_carret(50, 0x000001, 0x000002)  # kill carret 2 of player 1
