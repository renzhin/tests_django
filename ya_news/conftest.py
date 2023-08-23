import pytest

from datetime import datetime, timedelta

from django.utils import timezone

from news.models import News, Comment
from news.forms import BAD_WORDS


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
