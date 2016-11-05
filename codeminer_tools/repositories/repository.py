import os


def change_dir(function):
    def wrap_inner(*args, **kwargs):
        self = args[0]
        old_path = os.getcwd()
        os.chdir(self.path)
        result = function(*args, **kwargs)
        os.chdir(old_path)
        return result
    return wrap_inner


class Repository:
    def __init__(self, username=None, password=None, workspace=None):
        self.username = username if username else None
        self.password = password if password else None
        self.workspace = workspace if workspace else None