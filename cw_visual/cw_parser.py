from typing import List

from cw_visual.state_manager import CorewarStateManager

# separator symbol
separator = '"'

command_parsers = {
    # dict of command parsers
    # filled through @parser_for_command decorator
    # e.g.
    # 'k': kill_cursor
}


def parser_for_command(id: str):
    """decorator - makes decorated func to be a parser func for the command specified by 'id'"""
    def decorator(parse_fcn):
        command_parsers[id] = parse_fcn
        return parse_fcn

    return decorator


@parser_for_command('p')
def add_player(state_manager: CorewarStateManager, args: list):
    cycle = args[0]
    player_id = args[1]
    name = args[2]
    address = int(args[3])
    bytes_str = args[4]

    state_manager.add_player(player_id, name)
    state_manager.write_bytes(player_id, address, bytes_str)


@parser_for_command('c')
def add_cursor(state_manager: CorewarStateManager, args: list):
    cycle = args[0]
    player_id = args[1]
    carriage_id = args[2]
    address = int(args[3])

    state_manager.add_cursor(player_id, carriage_id, address)


@parser_for_command('k')
def kill_cursor(state_manager: CorewarStateManager, args: list):
    cycle = args[0]
    player_id = args[1]
    carriage_id = args[2]

    state_manager.kill_cursor(player_id, carriage_id)


@parser_for_command('m')
def move_cursor(state_manager: CorewarStateManager, args: list):
    cycle = args[0]
    player_id = args[1]
    carriage_id = args[2]
    offset = int(args[3])

    state_manager.move_cursor(player_id, carriage_id, offset)


@parser_for_command('w')
def write_memory(state_manager: CorewarStateManager, args: list):
    cycle = args[0]
    player_id = args[1]
    address = int(args[2])
    bytes = args[3]

    state_manager.write_bytes(player_id, address, bytes)


@parser_for_command('e')
def declare_winner(state_manager: CorewarStateManager, args: list):
    cycle = args[0]
    player_id = args[1]

    state_manager.declare_winner(player_id)


def unknown_command(line):
    print("unknown command: " + line)


class CorewarParser:
    """
    parses the output from corewar virtual machine.
    updates the state of memory, players and cursors through state_manager
    """

    def __init__(self, corewar_state_manager: CorewarStateManager):
        self.state_manager = corewar_state_manager

    def parse_corewar_output(self, lines: List[str]):
        for line in lines:
            tokens = line.split(separator)

            # first token is the command id
            command_id = tokens[0]
            # the rest of the tokens are arguments to the command
            args = tokens[1:]

            parse_fcn = command_parsers.get(command_id, None)

            if parse_fcn:
                parse_fcn(self.state_manager, args)
            else:
                unknown_command(line)
