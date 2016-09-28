import subprocess

class CommandLineClient:
    def __init__(self, command, env={}):
        self.command = command
        self.env = env

    def run_subcommand(self, subcommand, *args, flags=[], cwd=None, pipe_out=None, **kwargs):
        command = [self.command, subcommand]
        for arg in args:
            command.append(arg)

        if flags:
            for flag in flags:
                dashes = '-' if len(flag) == 1 else '--'
                command.append('{dashes}{flag}'.format(dashes=dashes, flag=flag))

        for flag, value in kwargs.items():
            dashes = '-' if len(flag) == 1 else '--'
            command.append('{dashes}{flag}'.format(dashes=dashes, flag=flag))
            command.append(value)

        print('$ {command}'.format(command=' '.join(command)))

        if pipe_out is None:
            result = subprocess.run(command, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, cwd=cwd, env=self.env)
        else:
            p1 = subprocess.Popen(command, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, cwd=cwd, env=self.env)
            p2 = pipe_out(p1.stdout, cwd, self.env)
            p1.stdout.close()
            p1.stderr.close()
            out, error = p2.communicate()
            return out, error

        return result.stdout, result.stderr
