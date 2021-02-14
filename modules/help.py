import constants
import command
from typing import List, Tuple, Optional
from snakecord import Message, Embed

commands = constants.loader.get_global('commands')
client = constants.loader.get_global('client')


def get_docs() -> List[Tuple[str]]:
    cmds = []
    for name, cmd in commands.commands.items():
        invocation = cmd.__invocation__
        if invocation is None:
            invocation = f'{commands.prefix}{name}'

        docs = cmd.__doc__
        if docs is None:
            docs = 'Not documented'

        cmds.append((invocation, docs))
    return cmds


async def send_help(message: Message, cmd: str):
    cmd = commands.get_command(cmd)
    if cmd is None:
        raise command.CommandError('That command doesn\'t exist')
    await cmd.send_help(message)


@command.invocation(
    f'{commands.prefix}help [cmd]'
)
@command.doc(
    'Sends this message if no command is provided '
    'otherwise sends the command\'s help message'
)
@commands.command
async def help(message: Message, cmd: Optional[str] = None) -> None:
    if cmd is not None:
        return await send_help(message, cmd)

    embed = Embed(title='Help', color=constants.BLUE)
    embed.set_footer(f'Type {commands.prefix}help <command>')

    for invocation, docs in get_docs():
        embed.add_field(invocation, docs)

    await message.channel.send(embed=embed)
