from pathlib import Path
from types import SimpleNamespace
from typing import AnyStr
from pathlib import Path

from langcodes import standardize_tag
from langcodes.tag_parser import LanguageTagError


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


def text_is_not_blank(text):
    if not text:
        return 'Input can not be blank.'
    return True


def folder_exists(folder_path):
    path_obj = Path(folder_path)
    if not folder_path.file_exists():
        return '{} does not exist'.format(folder_path)
    if not path_obj.is_dir():
        return '{} is not a folder'.format(folder_path)
    return True


def is_valid_lang_code(lang_code):
    try:
        standardize_tag(lang_code)
    except LanguageTagError:
        return '{} is not a valid language code.'.format(lang_code)
    return True


class ZendMdError(Exception):
    pass


cli_validators = SimpleNamespace(is_valid_lang_code=is_valid_lang_code, folder_exists=folder_exists,
                                 text_is_not_blank=text_is_not_blank)



