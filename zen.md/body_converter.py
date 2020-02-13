from pathlib import Path

from local_objects import LocalArticle, ZenMdProject
from utils import ZendMdError


def convert_images(article, project: ZenMdProject):
    """
    Unfortunatly Zendesk does not support updating attachments on an article. So we have to delete all the attachments,
    reupload and  updates the links to use the url with the new attachment ID..
    :param article:
    :param project:
    :return:
    """
    img_tags = article.body.find_all('img')
    delete_old_images(article, project)
    [update_image_tag(tag, article, project) for tag in img_tags]


def delete_old_images(article, project: ZenMdProject):
    old_attachments = project.zdesk_client.help_center_article_attachments(article.id)
    for attachment in old_attachments.data.get('article_attachments'):
        project.zdesk_client.help_center_articles_attachment_delete(attachment['id'])


def update_image_tag(img_tag, article, project):
    img_fn, attachment_id = upload_image(img_tag, article, project)
    attachment_url = '/hc/article_attachments/{}/{}'.format(attachment_id, img_fn)
    img_tag['href'] = img_fn
    return img_tag


def upload_image(img_tag, article, project: ZenMdProject):
    img_path = article.dir / Path(img_tag['href'])
    attachment_ids = {}
    file_obj = open(img_path.resolve(), 'rb')
    response = project.zdesk_client.help_center_article_attachment_create(article.id, {'inline': True},
                                                                          files={'file': (img_path.name, file_obj)})
    attachment_id = response.data['article_attachment']['id']
    return img_path.name, attachment_id


def convert_linked_articles(article, project, ignore_missing=False):
    article_tags = article.body.find_all('a')
    [update_article_tag(tag, article, project, ignore_missing) for tag in article_tags]


def update_article_tag(tag, article, project, ignore_missing):
    article_id = get_linked_article_id(tag, article, project)
    if article_id:
        article_url = '/hc/{}/articles/{}'.format(project.locale, article_id)
        tag['href'] = article_url
        return tag
    if ignore_missing:
        return tag
    raise ZendMdError('Article {} not yet saved and ignore-missing is False.'.format(tag['href']))


def get_linked_article_id(linked_article_tag, article, project):
    linked_article_path = Path(linked_article_tag['href'])
    parent_dir = project.root_dir if linked_article_path.is_absolute() else article.dir
    full_article_path = parent_dir / linked_article_path
    article_id = project.article_store.get_article_id(full_article_path)
    return article_id
