from snakecord import Message, Embed


class CommandError(Exception):
    def __init__(
        self,
        msg: str,
        message: Message,
        should_send: bool = True
    ) -> None:
        self.msg = msg
        self.message = message
        self.should_send = should_send

    async def send(self):
        embed = Embed(title='**Error**', description=self.msg)
        await self.message.channel.send(embed=embed)


class Command:
    def __init__(self, func, name=None):
        self.name = name or func.__name__
        self.aliases = []
        self.func = func
        self.help_func = None
        self.__doc__ = None
        self.__invocation__ = None

    def help(self, func):
        self.help_func = func

    async def send_help(self, message: Message):
        if self.help_func is None:
            raise CommandError(
                'This command has no help message',
                message
            )
        await self.help_func(message)

    async def call(self, *args):
        try:
            await self.func(*args)
        except CommandError as e:
            await e.send()


class CommandTable:
    def __init__(self, prefix, ignore_case=False, sep=' '):
        assert sep, 'Empty seperator'
        self.sep = sep
        self.prefix = prefix
        self.commands = {}
        self.ignore_case = ignore_case

    def command(self, func):
        cmd = Command(func)
        self.add_command(cmd)
        return cmd

    def get_command(self, name):
        return self.commands.get(name)

    def add_command(self, command):
        self.commands[command.name] = command
        for alias in command.aliases:
            self.commands[alias] = command

    def remove_command(self, command):
        self.commands.pop(command.name)
        for alias in command.aliases:
            self.commands.pop(alias)

    def _check_prefix(self, string, prefix):
        if not isinstance(prefix, str):
            raise TypeError('Prefix should be a string')
        if string.startswith(prefix):
            return prefix
        return None

    def check_prefix(self, message):
        prefix = self.prefix
        if callable(self.prefix):
            prefix = self.prefix(message)

        if not isinstance(prefix, str):
            for prefix in prefix:
                if self._check_prefix(message.content, prefix):
                    return prefix
            return None

        return self._check_prefix(message.content, prefix)

    async def handle(self, message):
        if message.author.user.bot:
            return

        prefix = self.check_prefix(message)
        if prefix is None:
            return None

        args = message.content[len(prefix):].split(self.sep)
        name = args.pop(0)

        if self.ignore_case:
            name = name.lower()

        command = self.get_command(name)
        if command is None:
            return None

        return await command.call(message, *args)


def doc(doc):
    def wrapped(cmd):
        cmd.__doc__ = doc
        return cmd
    return wrapped


def invocation(doc):
    def wrapped(cmd):
        cmd.__invocation__ = doc
        return cmd
    return wrapped
