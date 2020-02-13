import os

import inquirer
from zdesk import Zendesk

ZENMD_USER_ENV = 'ZENMD_USER'
ZENMD_PWD_ENV = 'ZENMD_PWD'
NOT_FOUND = -1


class ZenDeskClient(Zendesk):

    def get_user_segment_id(self, user_segment_name):
        """
        Convenience method for getting the id of a user segment from the name.
        """
        # A null user segment is valid, means everyone can access the article
        if user_segment_name is None:
            return None
        user_segments = self.help_center_user_segments_list(get_all_pages=True)
        name_map = {i['name']: i['id'] for i in user_segments.get('user_segments', [])}
        return name_map.get(user_segment_name, NOT_FOUND)

    def get_permission_group_id(self, permission_group_name):
        """
        Convenience method for getting the id of a permission group from the name.
        """

        #  The zdesk lib auto-genernates functions from the api docs. The current version hasn't been regenerated
        #  recently enough to include the permission_groups endpoint so we use the "call" function directly instead.
        api_path = "/api/v2/guide/permission_groups.json"
        perm_groups = self.call(api_path, get_all_pages=True)
        name_map = {i['name']: i['id'] for i in perm_groups.get('permission_groups', [])}
        return name_map.get(permission_group_name, NOT_FOUND)

    def get_section_id(self, section_name):
        pass

    def get_attachment_filenames(self, article_id):
        response = self.help_center_article_attachments(article_id, get_all_pages=True)
        return [i["file_name"] for i in response.data.get('article_attachments', [])]
        pass


def get_zendesk_credentials():
    """Use env credentials if provided """
    email_from_env, password_from_env = check_env_for_credentials()
    env_creds_provided = all([email_from_env, password_from_env])
    if not env_creds_provided:
        return ask_for_credentials()
    return email_from_env, password_from_env


def check_env_for_credentials():
    """Get the zendesk credentials user set as enviroment variables."""
    zendesk_email = os.environ.get(ZENMD_USER_ENV)
    zendesk_passowrd = os.environ.get(ZENMD_PWD_ENV)
    return zendesk_email, zendesk_passowrd


def ask_for_credentials():
    """Use the CLI to get the zendesk credentials """
    questions = [
        inquirer.text(name='zendesk_email', message='Enter your Zendesk email.'),
        inquirer.text(name='zendesk_email', message='Enter your Zendesk email.'),
    ]
    return inquirer.prompt(questions)