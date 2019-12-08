from typing import List, AnyStr

from utils import get_filename
from pathlib import Path

ARTICLE_URL_TEMPLATE = '/hc/{locale}/articles/{article_id}'
ARTICLE_ATTACHMENT_URL_TEMPLATE = '/hc/article_attachments/{article_id}/{filename}'


def convert_article(article: 'Article'):
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
    import pdb
    pdb.set_trace()
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
