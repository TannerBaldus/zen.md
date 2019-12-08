from typing import AnyStr, Callable

from bs4 import BeautifulSoup
import pytest

import article_parser


def test_update_image_tags():
    img_tags = [{'src': 'media/duck.jpg'}, {'src': 'media/moose.png'}]
    article_id = 1
    article_parser.update_image_tag_urls(img_tags, article_id)
    assert img_tags[0]['src'] == '/hc/article_attachments/{}/duck.jpg'.format(article_id)
    assert img_tags[1]['src'] == '/hc/article_attachments/{}/moose.png'.format(article_id)


def test_get_unattached_images():
    attached_images = ['duck.jpg']
    img_tags = [{'src': 'media/duck.jpg'}, {'src': 'media/moose.png'}]
    result = article_parser.get_unattached_images(img_tags, attached_images)
    expected = ['moose.png']
    assert result == expected


def test_convert_images(mock_article_func: Callable, article_html: AnyStr):
    mocked_article = mock_article_func(article_id=1, attached_images=['duck.jpg'])

    soup = BeautifulSoup(article_html)
    article_parser.convert_images(mocked_article, soup)

    expected = ['/hc/article_attachments/{}/duck.jpg'.format(mocked_article.zendesk_id),
     '/hc/article_attachments/{}/moose.png'.format(mocked_article.zendesk_id)]
    result = [i['src'] for i in soup.find_all('img')]
    assert sorted(result) == sorted(expected)
    mocked_article.attach_images.assert_called_once_with(['moose.png'])


@pytest.mark.parametrize('url,expected',
                         [('https://google.com', False), ('mailto:foo@bar.com', False),
                          ('#Title', False), ('//Arg', False), ('devs/api_usage.md', True)]
                         )
def test_is_article_link(url: AnyStr, expected: bool):
    assert article_parser.is_article_link(url) == expected


def test_get_article_links():
    mock_tags = [{"href": 'https://google.com'}, {"href": 'mailto:foo@bar.com'},
                 {"href": '#Title'}, {"href": '//Arg'}, {"href": 'devs/api_usage.md'}]
    result = article_parser.get_article_links(mock_tags)
    assert result == [{"href": 'devs/api_usage.md'}]


def test_update_link_hrefs(mock_article_func: Callable):
    mocked_article = mock_article_func(related_articles={'devs/api_usage.md': 1, 'help/starting.md': 2})
    mock_tags = [{"href": 'devs/api_usage.md'}, {"href": 'help/starting.md'}]
    article_parser.update_link_hrefs(mocked_article, mock_tags)
    assert mock_tags[0]['href'] == '/hc/en-US/articles/1'
    assert mock_tags[1]['href'] == '/hc/en-US/articles/2'
    mocked_article.get_related_article_id.assert_any_call('devs/api_usage.md')
    mocked_article.get_related_article_id.assert_any_call('help/starting.md')

