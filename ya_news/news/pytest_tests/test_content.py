import pytest

from django.conf import settings
from django.urls import reverse

HOME_URL = reverse('news:home')


def get_news_detail_url(news_id):
    return reverse('news:detail', args=(news_id,))


@pytest.mark.django_db
def test_max_news_on_home_page(client, create_many_news):
    create_many_news(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    response = client.get(HOME_URL)
    assert response.status_code == 200
    assert len(
        response.context['news_list']
    ) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, create_many_comments, author, news):
    create_many_comments(10, author, news)
    url = get_news_detail_url(news.id)
    response = client.get(url)
    object_list = response.context['news'].comment_set.all()
    all_dates = [comment.created for comment in object_list]
    sorted_dates = sorted(all_dates, reverse=False)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    url = get_news_detail_url(news.id)
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(admin_client, news):
    url = get_news_detail_url(news.id)
    response = admin_client.get(url)
    assert 'form' in response.context
