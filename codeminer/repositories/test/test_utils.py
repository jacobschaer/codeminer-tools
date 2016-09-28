import shlex
import subprocess

def run_shell_command(command, cwd=None, output=False, env=None):
    if cwd:
        print("$ cd {path}".format(path=cwd))
    print("$ {cmd}".format(cmd=command))
    args = shlex.split(command)

    stdout = subprocess.PIPE if output else None
    stderr = subprocess.PIPE if output else None

    return subprocess.run(args, cwd=cwd, stdout=stdout, stderr=stderr, env=env)