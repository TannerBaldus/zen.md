from typing import List, AnyStr
from dataclasses import dataclass

from utils import get_filename, ZendMdError
from pathlib import Path
from local_objects import ZenMdProject, LocalArticle
from zendesk_connection import ZenDeskClient

ARTICLE_URL_TEMPLATE = '/hc/{locale}/articles/{article_id}'
ARTICLE_ATTACHMENT_URL_TEMPLATE = '/hc/article_attachments/{article_id}/{filename}'


@dataclass
class ZdeskMetadata(object):
    title: str
    section_id: int
    user_segment_id: int
    permission_group_id: int
    comments_disabled: bool = None
    label_names: list[str] = None
    draft: bool = None
    promoted: bool = None
    position: int = None


def convert_metadata(article: LocalArticle,  zdesk_client: ZenDeskClient):
    """
    We want the user to be able to set the section, user_segment and permission_group of the article by name.
    However the api expects an id, so we use the api to get the id from the name.
    """
    local_metadata = article.metadata
    section_id = zdesk_client.get_section_id(local_metadata.section)
    if not section_id:
        raise ZendMdError()
    user_segment_id = zdesk_client.get_user_segment_id(local_metadata.user_segment)
    if not user_segment_id:
        raise ZendMdError()
    permission_group_id = zdesk_client.get_permission_group_id(local_metadata.permission_group)
    if not permission_group_id:
        raise ZendMdError()
    zdesk_metadata = ZdeskMetadata(local_metadata.title, section_id, user_segment_id, permission_group_id,
                                   local_metadata.comments_disabled, local_metadata.label_names, local_metadata.draft,
                                   local_metadata.promoted, local_metadata.position)

    return zdesk_metadata


def convert_article_body(article: 'Article'):
    html_body = article.body
    convert_images(article, html_body)
    convert_links(article, html_body)


def convert_links(article: 'Article', soup):
    """
     In the markdown the end user links to other articles via a file path e.g. developers/api_usage.md
     We need to convert these links to the appropriate Zendesk url of the format
    """
    anchor_tags = soup.findall('a')
    article_links = get_article_links(anchor_tags)
    update_link_hrefs(article_links)


def update_link_hrefs(article: 'Article', anchor_tags):
    for anchor_tag in anchor_tags:
        href = anchor_tag['href']
        related_article_id = article.get_related_article_id(href)
        updated_url = ARTICLE_URL_TEMPLATE.format(article_id=related_article_id,
                                                  locale=article.locale)
        anchor_tag['href'] = updated_url
    return anchor_tags


def get_article_links(anchor_tags: List):
    result_tags = [a for a in anchor_tags if is_article_link(a['href'])]
    return result_tags


def is_article_link(url: AnyStr):
    not_paragraph_link = bool(Path(url).stem.split("#")[0])
    not_external_protocol = all(i not in url for i in ["//", "mailto"])
    return not_paragraph_link and not_external_protocol


def convert_images(article: 'Article', soup):
    """
    The end user references images by file path. So we need to upload/attach all the images referenced in the article.
    And change the image sources to the appropriate Zendesk url for attachments of
    the format /hc/article_attachments/{article_id}/{filename}
    """

    img_tags = soup.find_all('img')
    unattached_images = get_unattached_images(img_tags, article.attached_images)

    article.attach_images(unattached_images)
    update_image_tag_urls(img_tags, article.zendesk_id)


def update_image_tag_urls(img_tags: List, article_id):
    """
    All of the images should have been uploaded/attached to the article already.
    So we can just change the src to the correct Zendesk url.

    """
    for img_tag in img_tags:
        image_fn = get_filename(img_tag['src'])
        new_src = ARTICLE_ATTACHMENT_URL_TEMPLATE.format(article_id=article_id, filename=image_fn)
        img_tag['src'] = new_src
    return img_tags


def get_unattached_images(img_tags: List, attached_images: List) -> List[AnyStr]:
    """
    Finds all image tags whose src image is not uploaded and attached to the current article.
    """
    new_images = []
    for image_tag in img_tags:
        image_fn = get_filename(image_tag['src'])
        if image_fn not in attached_images:
            new_images.append(image_fn)
    return new_images
