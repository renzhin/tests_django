# test_content.py
import pytest

from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
def test_max_news_on_home_page(client, create_many_news):
    # Создайте более 10 новостей в базе данных с помощью фикстуры create_news.
    create_many_news(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    # Выполните GET-запрос на главную страницу.
    response = client.get(reverse('news:home'))
    # Проверьте, что статус код ответа равен 200 (OK).
    assert response.status_code == 200
    # Проверьте, что на странице не более 10 новостей.
    assert len(
        response.context['news_list']
    ) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    # Получаем даты новостей в том порядке, как они выведены на странице.
    all_dates = [news.date for news in object_list]
    # Сортируем полученный список по убыванию.
    sorted_dates = sorted(all_dates, reverse=True)
    # Проверяем, что исходный список был отсортирован правильно.
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(admin_client, news):
    url = reverse('news:detail', args=(news.id,))
    response = admin_client.get(url)
    assert 'form' in response.context


# @pytest.mark.django_db
# def test_comments_order(client, news):
#     url = reverse('news:detail', args=(news.id,))
#     response = client.get(url)
#     # Проверяем, что объект новости находится в словаре контекста
#     # под ожидаемым именем - названием модели.
#     assert 'news' in response.context
#     # Получаем объект новости.
#     news = response.context['news']
#     # Получаем все комментарии к новости.
#     all_comments = news.comment_set.all()
#     print("Number of comments:", news.comment_set.count())
#     # Проверяем, что время создания первого комментария в списке
#     # меньше, чем время создания второго.
#     assert all_comments[0].created < all_comments[1].created


# @pytest.mark.django_db
# def test_comments_order(client, news, create_many_comments):
#     create_many_comments(2)
#     url = reverse('news:detail', args=(news.id,))
#     response = client.get(url)
#     # Проверяем, что объект новости находится в словаре контекста
#     # под ожидаемым именем - названием модели.
#     assert 'news' in response.context
#     # Получаем объект новости.
#     news = response.context['news']
#     # Получаем все комментарии к новости.
#     all_comments = news.comment_set.all()
#     # Проверяем, что время создания первого комментария в списке
#     # меньше, чем время создания второго.
#     assert all_comments[0].created < all_comments[1].created
