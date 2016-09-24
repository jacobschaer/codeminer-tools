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
    pass