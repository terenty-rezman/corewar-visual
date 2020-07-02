from corewar_state_manager import CorewarStateManager

# separator symbol
separator = '"'

command_parsers = {
    # dict of command parsers
    # filled through @parser_for_command decorator
    # e.g.
    # 'k': kill_carret
}


def parser_for_command(id: str):
    """decorator - makes decorated func to be a parser func for the command specified by 'id'"""
    def decorator(parse_fcn):
        command_parsers[id] = parse_fcn
        return parse_fcn

    return decorator


@parser_for_command('p')
def add_player(state_manager: CorewarStateManager, args: list):
    player_name = args[0]
    address = int(args[1])
    bytes_str = args[2]

    state_manager.add_player(player_name)
    state_manager.write_bytes(player_name, address, bytes_str)


@parser_for_command('c')
def add_carret(state_manager: CorewarStateManager, args: list):
    player_name = args[0]
    carret_name = args[1]
    address = int(args[2])

    state_manager.add_carret(player_name, carret_name, address)


@parser_for_command('k')
def kill_carret(state_manager: CorewarStateManager, args: list):
    player_name = args[0]
    carret_name = args[1]

    state_manager.kill_carret(player_name, carret_name)


@parser_for_command('m')
def move_carret(state_manager: CorewarStateManager, args: list):
    player_name = args[0]
    carret_name = args[1]
    offset = int(args[2])

    state_manager.move_carret(player_name, carret_name, offset)


def unknown_command(line):
    print("unknown command: " + line)


class CorewarParser:
    """
    parses the output from corewar virtual machine.
    updates the state of memory, players and carrets through state_manager
    """

    def __init__(self, corewar_state_manager: CorewarStateManager):
        self.state_manager = corewar_state_manager

    def parser_corewar_output(self, line):
        params = line.split(separator)

        # first param is the command id
        command_id = params[0]
        # the rest of the params are arguments to the command
        args = params[1:]

        parse_fcn = command_parsers.get(command_id, None)

        if parse_fcn:
            parse_fcn(self.state_manager, args)
        else:
            unknown_command(line)
