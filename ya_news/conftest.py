# conftest.py
import pytest

from datetime import datetime, timedelta

from django.utils import timezone

from news.models import News, Comment

today = datetime.today()
now = timezone.now()


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):  # Вызываем фикстуру автора и клиента.
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def news():
    news = News.objects.create(  # Создаём объект заметки.
        text='Текст заметки',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
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


# @pytest.fixture
# def create_many_comments():

#     def _create_comments(count):
#         for i in range(count):
#             Comment.objects.create(
#                 news=news,
#                 author=author,
#                 text=f'Текст комментария {i}',
#             )
#             comment.created = now + timedelta(days=count)
#     return _create_comments

# @pytest.fixture
# def create_two_comments(news, author):
#     comment1 = Comment.objects.create(
#         news=news, author=author, text='Комментарий 1'
#     )
#     comment2 = Comment.objects.create(
#         news=news, author=author, text='Комментарий 2'
#     )
#     comment1.created = now + timedelta(days=1)
#     comment2.created = now + timedelta(days=2)
#     return comment1, comment2
