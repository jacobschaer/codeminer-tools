import subprocess

class CommandLineClient:
    def __init__(self, command, env={}):
        self.command = command
        self.env = env

    def run_subcommand(self, subcommand, *args, flags=[], cwd=None, stdin=None,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs):
        command = [self.command, subcommand]
        
        if flags:
            for flag in flags:
                dashes = '-' if len(flag) == 1 else '--'
                command.append('{dashes}{flag}'.format(dashes=dashes, flag=flag))

        for flag, value in kwargs.items():
            dashes = '-' if len(flag) == 1 else '--'
            command.append('{dashes}{flag}'.format(dashes=dashes, flag=flag))
            command.append(value)

        for arg in args:
            command.append(arg)

        print('$ {command}'.format(command=' '.join(command)))

        return subprocess.Popen(command, stdin=stdin, stdout=stdout,
            stderr=stderr, cwd=cwd, env=self.env)