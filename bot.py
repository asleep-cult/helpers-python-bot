import snakecord
import constants
from datetime import datetime


class Client(snakecord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.started_at = None
        constants.loader.set_global('client', self)
        constants.loader.add_module('modules.info')
        constants.loader.add_module('modules.reddit')
        constants.loader.add_module('modules.help')
        constants.loader.load()

    def start(self):
        self.started_at = datetime.now()
        super().start(constants.SETUP['TOKEN'])


client = Client()


@client.on
async def message_create(message):
    commands = constants.loader.get_global('commands')
    await commands.handle(message)

client.start()
