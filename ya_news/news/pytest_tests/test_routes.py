from http import HTTPStatus

import pytest
from django.conf import settings
from pytest_django.asserts import assertRedirects

URL_HOME = pytest.lazy_fixture('url_home')
URL_LOGOUT = pytest.lazy_fixture('url_logout')
URL_SIGNUP = pytest.lazy_fixture('url_signup')
URL_DETAIL = pytest.lazy_fixture('url_detail_news')
URL_LOGIN = settings.LOGIN_URL
URL_DELETE_COMMENT = pytest.lazy_fixture('url_delete_news')
URL_EDIT_COMMENT = pytest.lazy_fixture('url_edit_news')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
READER_CLIENT = pytest.lazy_fixture('admin_client')


@pytest.mark.parametrize(
    'url, expected_status, parametrized_client',
    (
        (URL_HOME, HTTPStatus.OK, None),
        (URL_LOGIN, HTTPStatus.OK, None),
        (URL_LOGOUT, HTTPStatus.OK, None),
        (URL_SIGNUP, HTTPStatus.OK, None),
        (URL_DETAIL, HTTPStatus.OK, None),
        (URL_DELETE_COMMENT, HTTPStatus.OK, AUTHOR_CLIENT),
        (URL_DELETE_COMMENT, HTTPStatus.NOT_FOUND, READER_CLIENT),
        (URL_EDIT_COMMENT, HTTPStatus.OK, AUTHOR_CLIENT),
        (URL_EDIT_COMMENT, HTTPStatus.NOT_FOUND, READER_CLIENT),
    )
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(
    client, url, comment, expected_status, parametrized_client
):
    if parametrized_client:
        client = parametrized_client
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (URL_DELETE_COMMENT, URL_EDIT_COMMENT)
)
@pytest.mark.django_db
def test_redirects_for_anonymous_user(client, url, comment):
    expected_url = f'{URL_LOGIN}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
