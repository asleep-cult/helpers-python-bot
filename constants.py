import json
from command import CommandTable, ModuleLoader

loader = ModuleLoader()
loader.set_global('commands', CommandTable('>'))

BLUE = 0x6adde6
REPOSITORY = 'https://github.com/asleep-cult/helpers-python-bot/'

with open('setup.json') as fp:
    SETUP = json.load(fp)
