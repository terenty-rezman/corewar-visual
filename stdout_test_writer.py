#!/usr/bin/env python3

import time
import sys
import functools

# this script emulates output of corewar vm to stdout
# used to test corewar_visual in abscence of corewar vm

sep = '"'  # separator sign


def add_player(name, address, bytes):
    sys.stdout.write(
        f'p{sep}{name}{sep}{address}{sep}{bytes}\n'
    )

    sys.stdout.flush()


def add_carret(pl_name, ca_name, address):
    sys.stdout.write(
        f'c{sep}{pl_name}{sep}{ca_name}{sep}{address}\n'
    )

    sys.stdout.flush()


def kill_carret(pl_name, ca_name):
    sys.stdout.write(
        f'k{sep}{pl_name}{sep}{ca_name}\n'
    )

    sys.stdout.flush()


def move_carret(pl_name, ca_name, offset):
    sys.stdout.write(
        f'm{sep}{pl_name}{sep}{ca_name}{sep}{offset}\n'
    )

    sys.stdout.flush()


sleep = functools.partial(time.sleep, 2)

# start emulating output of corewar vm to stdout
add_player('Batman', 0, "00002901DA04446963742901DA")
add_player('Robin', 64*10, "df01bb09")
add_player('Yoshi', 64*20, "47823958")
add_player('Mario', 64*50, "44ff55eeaabbcacd9933")

add_carret('Batman', 'c1', 0)
add_carret('Robin', 'c1', 64*10)
add_carret('Yoshi', 'c1', 64*20)
add_carret('Mario', 'c1', 64*50)

add_carret('Batman', 'c2', 64*13)

move_carret('Batman', 'c2', 4)
move_carret('Batman', 'c2', 4)

kill_carret('Batman', 'c2')
