from calc_cmd import calc_cmd
from ddg_cmd import query_ddg
from rand_cmd import rand_cmd


async def help_cmd(client, message, args):
    msg = "Available commands:\n[" + ", ".join(commands.keys()) + "]"
    return msg

async def test_command(client, message, args):
    return 'testing, args: ' + args

commands = {
    'test': test_command,
    'help': help_cmd,
    'calc': calc_cmd,
    'rand': rand_cmd,
    'ddg': query_ddg,
}
