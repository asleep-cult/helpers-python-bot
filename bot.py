import snekcord
import constants
from datetime import datetime


class Client(snekcord.WebSocketClient):
    def __init__(self, *args, **kwargs):
        super().__init__(token='Bot ' + constants.SETUP['TOKEN'], *args, **kwargs)

        self.started_at = None
        constants.loader.set_global('client', self)
        constants.loader.add_module('modules.info')
        constants.loader.add_module('modules.reddit')
        constants.loader.add_module('modules.help')
        constants.loader.load()

    def run_forever(self):
        self.started_at = datetime.now()
        super().run_forever()


client = Client()


@client.on()
async def message_create(evt):
    commands = constants.loader.get_global('commands')
    await commands.handle(evt)


client.run_forever()
