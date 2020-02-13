
from __future__ import print_function, unicode_literals
from pathlib import Path
from typing import Dict
import os

import inquirer
import fire

from utils.cli_validators import *
from zendesk_connection import get_zdesk_client


def create_site_config():
    site_data = ask_for_site_data()
    zdesk_client = get_zdesk_client(site_data['url'])


def ask_for_site_data() -> Dict:
    questions = [
        inquirer.text('url', message='Enter your Zendesk site_url.',  validate=text_is_not_blank),
        inquirer.text('locale', message='What is the default locale (lang code) for the site?\nDefault is en-us',
                      default='en-us', validate=is_valid_lang_code)
    ]
    return inquirer.prompt(questions)


def create_section(directory=None):
    section_dir = directory or os.getcwd()


def ask_for_section_data():
    zdesk_client = get_zdesk_client()
    questions = [
        {
            'type': 'input',
            'name': 'folder_path',
            'message': 'Where is your doc project root. Default is the cwd.',
            'default': Path.cwd(),
            'validate': folder_exists,
        },
        {
            'type': 'input',
            'name': 'locale',
            'message': 'What is the default locale (lang code) for the site?\nDefault is en-us',
            'default': 'en-us',
            'validate': is_valid_lang_code
        }
    ]


if __name__ == 'main':
    fire.Fire({'make_site_root': create_site_config,
               'make_section': create_section})
