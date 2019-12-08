from pathlib import Path
from typing import AnyStr

def get_filename(file_path: AnyStr):
    """
    In the markdown the src will be media/example.jpg.
    We need to extract just the file name for dealing with files in Zendesk.
    """
    path = Path(file_path)
    return path.name


def get_containing_dir(file_path: AnyStr):
    path = Path(file_path)
    return path.parent.name
