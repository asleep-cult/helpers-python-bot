import os
import gc
import asyncio
import threading
import constants
from snakecord import Message, Embed

commands = constants.commands
ICON_URL = 'https://cdn.discordapp.com/icons/%s/%s.png'


@commands.command
async def ping(message: Message) -> None:
    shard = message.guild.shard
    embed = Embed(
        title=':ping_pong: Ping',
        description=(
            f'**Shard {shard.id}**\n'
            f'Websocket Latency: {(shard.websocket.latency * 1000):.2f}ms'
        ),
        color=constants.BLUE
    )
    await message.channel.send(embed=embed)


@commands.command
async def info(message: Message) -> None:
    threads = threading.active_count()
    tasks = asyncio.all_tasks()
    collected = sum(gen['collected'] for gen in gc.get_stats())
    embed = Embed(
        title='Info',
        description=(
            f'**Process ID**: {os.getpid()}\n'
            f'**Active Threads**: {threads}\n'
            f'**Asyncio Tasks**: {len(tasks)}\n'
            f'**Garbage Collected Objects**: {collected}\n'
        ),
        color=constants.BLUE
    )
    await message.channel.send(embed=embed)
