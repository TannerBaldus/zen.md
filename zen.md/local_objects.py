from pathlib import Path
from dataclasses import dataclass

import frontmatter
from configobj import ConfigObj
from tinydb import TinyDB, Query

from utils import ZendMdError
from zendesk_connection import ZenDeskClient

ARTICLE_STORE_FN = Path('_articles.json')
SITE_CONFIG_FN = Path('_zenmd.ini')

@dataclass
class ArticleMetaData(object):
    title: str
    section: str
    user_segment: str
    permission_group: str
    comments_disabled: bool = None
    label_names: list[str] = None
    draft: bool = None
    promoted: bool = None
    position: int = None


@dataclass
class LocalArticle:
    file_path: Path
    metadata: ArticleMetaData
    body: str

    @classmethod
    def from_file_path(cls, file_path: str):
        file_path_obj: Path = Path(file_path).resolve()
        cls.validate_file_path(file_path)
        file_obj = open(file_path)
        metadata_dict, body = frontmatter.load(file_obj)
        metadata = ArticleMetaData(**metadata_dict)
        return cls(file_path, metadata, body)

    @property
    def section_name(self):
        return self.file_path.parent.name

    @property
    def filename(self):
        return self.file_path.name

    @classmethod
    def validate_file_path(cls, file_path: Path):
        if not file_path.exists():
            raise ZendMdError('{} does not exist.'.format(file_path))
        if not file_path.is_file():
            raise ZendMdError('{} is not a file.'.format(file_path))


class ArticleStore(object):
    def __init__(self, json_path: Path):
        self.db = TinyDB(json_path)

    def get_article_id(self, file_path: Path):
        Article = Query()
        results = self.db.search(Article.folder == section_name, Article.filename == article_filename)
        if not len(results):
            return None
        article_id = results[0]['zen_id']
        return article_id

    def save_article_id(self, section_name, article_filename, article_id):
        Article = Query()
        self.db.upsert({'section': section_name, 'filename': article_filename, 'zen_id': article_id},
                       Article.section == section_name, Article.filename == article_filename)


class SiteConfig(object):
    file_name = '_zenmd.ini'
    site_url_keyword = 'site_url'

    def __init__(self, filename):
        self.config_obj = ConfigObj(filename)

    @property
    def site_url(self):
        return self.config_obj[self.site_url_keyword]

    @site_url.setter
    def site_url(self, site_url):
        self.config_obj[self.site_url_keyword] = site_url
        self.config_obj.write()

    @property
    def locale(self):
        return self.config_obj['locale']

    @locale.setter
    def locale(self, locale):
        self.config_obj['locale'] = locale
        self.config_obj.write()

@dataclass
class ZenMdProject(object):
    root_dir: Path
    site_config: SiteConfig
    article_store: ArticleStore
    zdesk_client: ZenDeskClient

    @classmethod
    def new_project(cls, dir_path, site_url, locale):
        site_config_path = Path(dir_path)/SITE_CONFIG_FN
        article_store_path = Path(dir_path)/ARTICLE_STORE_FN
        site_config_path.touch()
        article_store_path.touch()
        site_config = SiteConfig(site_config_path)
        site_config.site_url = site_url
        site_config.locale = locale

    @classmethod
    def load_from_dir(cls, dir, zdesk_creds):
        project_root_dir = cls.find_project_root()
        site_config_path = Path(project_root_dir)/SITE_CONFIG_FN
        article_store_path = Path(project_root_dir)/ARTICLE_STORE_FN
        return cls()

    @classmethod
    def find_project_root(cls, start_dir):
        return Path()

    def get_section_article_ids(self, section_name, filename):
        section_id = self.site_config.get_section(section_name)
        article_id = self.article_store.get_article_id(section_name, filename)
        return section_id, article_id

