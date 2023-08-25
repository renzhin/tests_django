from http import HTTPStatus

import pytest
from django.conf import settings


@pytest.mark.django_db
def test_max_news_on_home_page(client, create_many_news, url_home):
    create_many_news(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    response = client.get(url_home)
    assert response.status_code == HTTPStatus.OK
    assert len(
        response.context['news_list']
    ) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, url_home):
    response = client.get(url_home)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(
    client,
    create_many_comments,
    author,
    news,
    url_detail_news
):
    create_many_comments(10, author, news)
    response = client.get(url_detail_news)
    object_list = response.context['news'].comment_set.all()
    all_dates = [comment.created for comment in object_list]
    sorted_dates = sorted(all_dates, reverse=False)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_anonymous_client_has_no_form(
    client,
    url_detail_news,
):
    response = client.get(url_detail_news)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(
    admin_client,
    url_detail_news,
):
    response = admin_client.get(url_detail_news)
    assert 'form' in response.context
