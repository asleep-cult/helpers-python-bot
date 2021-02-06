import snakecord
import constants
import importlib

client = snakecord.Client()
importlib.import_module('modules.info')


@client.on
async def message_create(message):
    await constants.commands.handle(message)

client.start(constants.SETUP['TOKEN'])
