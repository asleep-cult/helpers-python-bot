import constants
from snakecord.message import Embed

commands = constants.commands
ICON_URL = 'https://cdn.discordapp.com/icons/%s/%s.png'


@commands.command
async def ping(message):
    shard = message.guild.shard
    await message.channel.send(
        '**Shard %s**\n'
        'Websocket Latency: %.2fms' % (
            shard.id,
            shard.websocket.latency * 1000
        )
    )


@commands.command
async def server(message):
    embed = Embed(title=message.guild.name, color=constants.BLUE)
    embed.set_thumbnail(ICON_URL % (message.guild.id, message.guild.icon))
    description = []
    description.append(
        '**Members**: {}'.format(len(message.guild.members))
    )
    description.append(
        '**Emojis**: {}'.format(len(message.guild.emojis))
    )
    embed.description = '\n'.join(description)
    await message.channel.send(embed=embed)
