import os

def resolve_path(path, is_dir=False):
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    if is_dir and not os.path.exists(path):
        os.makedirs(path)
    return path


 

