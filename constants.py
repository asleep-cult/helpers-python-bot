import json
from command import CommandTable

commands = CommandTable('!')

BLUE = 0x328aed

with open('setup.json') as fp:
    SETUP = json.load(fp)
