import shlex
import subprocess

def run_shell_command(command, cwd=None, wait=True, output=False):
    if cwd:
        print("$ cd {path}".format(path=cwd))
    print("$ {cmd}".format(cmd=command))
    args = shlex.split(command)

    stdout = subprocess.PIPE if output else None
    stderr = subprocess.PIPE if output else None

    if wait:
        return subprocess.run(args, cwd=cwd, stdout=stdout, stderr=stderr)
    else:
        return subprocess.Popen(args, cwd=cwd, stdout=stdout, stderr=stderr)