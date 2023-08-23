from http import HTTPStatus

import pytest

from django.conf import settings
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('url_home'),
        settings.LOGIN_URL,
        pytest.lazy_fixture('url_logout'),
        pytest.lazy_fixture('url_signup'),
        pytest.lazy_fixture('url_detail_news'),
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
        pytest.lazy_fixture('url_delete_news'),
        pytest.lazy_fixture('url_edit_news')
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
        pytest.lazy_fixture('url_delete_news'),
        pytest.lazy_fixture('url_edit_news')
    )
)
@pytest.mark.django_db
def test_redirects_for_anonymous_user(client, url, comment):
    expected_url = f'{settings.LOGIN_URL}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
