from local_objects import ArticleStore


def test_article_store(tmp_article_json):
    article_store = ArticleStore(tmp_article_json)
    get_result = article_store.get_article_id('general', 'getting_started.md')
    assert get_result == 1
    article_store.save_article_id('devs', 'api_usage.md', 2)
    insert_result = article_store.get_article_id('devs', 'api_usage.md')
    assert insert_result == 2
    article_store.save_article_id('general', 'getting_started.md', 3)
    upsert_result = article_store.get_article_id('general', 'getting_started.md')
    assert upsert_result == 3


def test_site_config():

    pass



