from http import HTTPStatus

import pytest

from django.conf import settings
from pytest_django.asserts import assertRedirects

URL_HOME = pytest.lazy_fixture('url_home')
URL_LOGOUT = pytest.lazy_fixture('url_logout')
URL_SIGNUP = pytest.lazy_fixture('url_signup')
URL_DETAIL = pytest.lazy_fixture('url_detail_news')
URL_LOGIN = settings.LOGIN_URL
URL_DELETE_NEWS = pytest.lazy_fixture('url_delete_news')
URL_EDIT_NEWS = pytest.lazy_fixture('url_edit_news')


@pytest.mark.parametrize(
    'url',
    (
        URL_HOME,
        URL_LOGIN,
        URL_LOGOUT,
        URL_SIGNUP,
        URL_DETAIL,
    )
)
@pytest.mark.django_db
def test_pages_and_detail_availability_for_anonymous_user(
    client, url
):
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url',
    (
        URL_DELETE_NEWS,
        URL_EDIT_NEWS,
    )
)
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND)
    ),
)
def test_comment_edit_and_delete(
        parametrized_client, url, comment, expected_status
):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        URL_DELETE_NEWS,
        URL_EDIT_NEWS,
    )
)
@pytest.mark.django_db
def test_redirects_for_anonymous_user(client, url, comment):
    expected_url = f'{URL_LOGIN}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
