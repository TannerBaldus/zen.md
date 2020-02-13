from unittest import mock
from typing import Callable, List, AnyStr, Dict
import pytest
from tinydb import TinyDB


@pytest.fixture
def mock_article_func() -> Callable[[int, List[AnyStr], List[AnyStr], Dict, AnyStr], mock.MagicMock]:

    def make_mocked_article(article_id: int = 1, attached_images: List[AnyStr] = [],
                            related_articles: Dict = {},
                            locale: AnyStr = 'en-US') -> mock.MagicMock:
        mocked_article = mock.MagicMock()
        mocked_article.get_related_article_id.side_effect = lambda i: related_articles[i]
        type(mocked_article).locale = mock.PropertyMock(return_value=locale)
        type(mocked_article).zendesk_id = mock.PropertyMock(return_value=article_id)
        type(mocked_article).attached_images = mock.PropertyMock(return_value=attached_images)
        return mocked_article

    return make_mocked_article


@pytest.fixture
def article_html():
    html_string = """
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
    <h2 id="cp">Lorem ipsum</h2>
    <ul>
    <li> Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.<a href="developers/api_usage.md">Camp</a>.)</li>
    <li> Excepteur sint occaecat cupidatat non proident, sunt in culpa qui  <em>Optional</em>.</li
    <li> Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.<a href="https://google.com">Goog</a>.)</li>
    </ul>
    <p> ed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco,
        <a href="mailto:foo@bar.com"></a>.</p>
    <h2 id="1">Lorem ipsum dolor sit amet,</h2>
    <p><img src="media/moose.png" width="400"></p>
    <blockquote>
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua</p>
    </blockquote>
    <p>OLorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut.</p>
    <ul>
    <li>Cairo moose <img src="media/duck.jpg" width="400"> on</a>.</li>
    <li> Fella <a href="//Aclass">Mapless Campaigns</a>.</li>
    <li>Snake</li>
    </ul>
    """
    return html_string


@pytest.fixture()
def tmp_article_json(tmp_path):
    json_file = tmp_path/'articles.json'
    json_file.touch()
    db = TinyDB(str(json_file))
    db.insert({'section': 'general', 'filename': 'getting_started.md', 'zen_id': 1})
    db.close()
    return json_file
