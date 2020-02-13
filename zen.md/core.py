from pathlib import Path
from dataclasses import dataclass, asdict
from copy import deepcopy

from zendesk_connection import ZenDeskClient, NOT_FOUND
from local_objects import LocalArticle, SiteConfig, ArticleStore, ArticleMetaData
from utils import ZendMdError

@dataclass
class ZenMdArticle(object):
    metadata: dict
    body = str
    section_id: int
    section_name: str
    zendesk_id: int
    filename: str

    @classmethod
    def from_article_path(cls, article_path: Path,  zen_md_project: ZenMdProject):
        local_article = LocalArticle(article_path)
        section_id = zen_md_project.site_config.get_section(local_article.section_name)
        if not section_id:
            raise ZendMdError('')
        zendesk_id = zen_md_project.article_store.get_article_id(local_article.section_name, local_article.filename)
        metadata = cls.convert_metadata(local_article.metadata, zen_md_project)
        return cls(metadata, section_id, local_article.section_name, zendesk_id, local_article.filename)

    @staticmethoda
    def convert_metadata(article_metadata: ArticleMetaData, zen_md_project: ZenMdProject):
        """
        Convert the end user set metadata to values expected by the Zendesk api.

        We don't want the end user to have to remember the numerical ids of their user segments and permission_groups
        so we let them use the names with the user_segment and permission_group field in the frontmatter of md docs.

        But the Zendesk api needs the numerical ids so we try and match the ids to the provided names and update the
        metadata to the proper api fields.
        """
        user_segment_id = zen_md_project.zdesk_client.get_user_segment_id(article_metadata.user_segment)
        permission_group_id = zen_md_project.zdesk_client.get_permission_group_id(article_metadata.permission_group)
        if user_segment_id == NOT_FOUND:
            raise ZendMdError('{} is not a valid user segment name.'.format(article_metadata.user_segment))
        if permission_group_id == NOT_FOUND:
            raise ZendMdError('{} is not a valid permission group name.'.format(article_metadata.user_segment))
        result = {'user_segment_id': user_segment_id, 'permission_group_id': permission_group_id}

        # The zendesk article api expects user_segment_id and permission_group_id fields, so we need to remove the
        # name fields
        invalid_fields = ['user_segment', 'permission_group']
        other_metadata = {k: v for k, v in asdict(article_metadata) if k not in invalid_fields}
        result.update(other_metadata)
        return result
