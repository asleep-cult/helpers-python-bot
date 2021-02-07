import json
from command import CommandTable

commands = CommandTable('>')

BLUE = 0x6adde6

with open('setup.json') as fp:
    SETUP = json.load(fp)
