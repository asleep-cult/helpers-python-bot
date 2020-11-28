import discord
from discord.ext import commands

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=".")

    async def on_ready(self):
        print("Bot is ready.")

    async def on_guild_join(guild):
        print("Joined {0.name}.".format(guild))

    async def on_guild_remove(guild):
        print("Left {0.name}.".format(guild))

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content == "Hello!":
            await message.channel.send("Hi! {0.author.mention}".format(message))

    def run(self):
        super().run("token here", bot=True, reconnect=True)

bot = Bot()
bot.run()