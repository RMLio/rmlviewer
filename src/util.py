import os

def resolve_path(path, is_dir=False):
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    if is_dir and not os.path.exists(path):
        os.makedirs(path)
    return path


def resolve_source_path(path, rml_root=None, mapping_dir=None):
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)

    if os.path.isabs(path):
        return path

    if str(rml_root) == 'http://w3id.org/rml/MappingDirectory' and mapping_dir:
        return os.path.abspath(os.path.join(mapping_dir, path))

    # If rml:root is omitted, the spec default is CurrentWorkingDirectory.
    return os.path.abspath(path)


 

