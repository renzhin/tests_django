import pytest

from http import HTTPStatus

from django.urls import reverse

from pytest_django.asserts import assertRedirects


@pytest.fixture
def id_for_args(news):
    return news.id,


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', pytest.lazy_fixture('id_for_args')),
    )
)
@pytest.mark.django_db
def test_pages_and_detail_availability_for_anonymous_user(
    client, name, args
):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_with_id',
    ('news:delete', 'news:edit')
)
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND)
    ),
)
def test_comment_edit_and_delete(
        parametrized_client, url_with_id, comment, expected_status
):
    url = reverse(url_with_id, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_with_id',
    ('news:delete', 'news:edit')
)
def test_redirects_for_anonymous_user(client, url_with_id, comment):
    login_url = reverse('users:login')
    url = reverse(url_with_id, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
