from datetime import datetime, timedelta

import pytest

from django.urls import reverse
from django.utils import timezone

from news.forms import BAD_WORDS
from news.models import Comment, News

today = datetime.today()
now = timezone.now()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        text='Текст заметки',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария ля ля',
    )
    return comment


@pytest.fixture
def create_many_news():

    def _create_news(count):
        for i in range(count):
            News.objects.create(
                text=f'Новость {i}',
                date=today - timedelta(days=count)
            )
    return _create_news


@pytest.fixture
def create_many_comments():

    def _create_comments(count, author, news):
        for i in range(count):
            comment = Comment.objects.create(
                news=news,
                author=author,
                text=f'Текст комментария {i}',
            )
            comment.created = now + timedelta(days=i + 1)
            comment.save()
    return _create_comments


@pytest.fixture
def form_data(news):
    return {
        'text': 'Новый текст',
        'news': news,
    }


@pytest.fixture
def bad_words_data():
    return {
        'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    }


@pytest.fixture
def url_home():
    return reverse('news:home')


@pytest.fixture
def url_logout():
    return reverse('users:logout')


@pytest.fixture
def url_signup():
    return reverse('users:signup')


@pytest.fixture
def news_id(news):
    return news.id,


@pytest.fixture
def url_detail_news(news_id):
    return reverse('news:detail', args=news_id)


@pytest.fixture
def url_edit_news(news_id):
    return reverse('news:edit', args=news_id)


@pytest.fixture
def url_delete_news(news_id):
    return reverse('news:delete', args=news_id)
