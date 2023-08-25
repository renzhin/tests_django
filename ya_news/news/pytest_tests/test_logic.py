from http import HTTPStatus

import pytest

from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import WARNING
from news.models import Comment


def test_user_can_create_comment(
    author_client,
    news,
    author,
    url_detail_news,
    form_data
):
    initial_comment_count = Comment.objects.filter(news=news).count()
    response = author_client.post(url_detail_news, data=form_data)
    assert response.status_code == 302
    assertRedirects(response, f'{url_detail_news}#comments')
    new_comment_count = Comment.objects.filter(news=news).count()
    assert new_comment_count == initial_comment_count + 1
    new_comment = Comment.objects.filter(news=news).latest('created')
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client,
    url_detail_news,
    form_data
):
    initial_comment_count = Comment.objects.count()
    client.post(url_detail_news, data=form_data)
    assert Comment.objects.count() == initial_comment_count


def test_user_cant_use_bad_words(
    author_client,
    url_detail_news,
    bad_words_data
):
    initial_comment_count = Comment.objects.count()
    response = author_client.post(url_detail_news, data=bad_words_data)

    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == initial_comment_count


def test_author_can_edit_note(
    author_client,
    author,
    form_data,
    news,
    url_detail_news,
    url_edit_news,
    comment
):
    response = author_client.post(url_edit_news, form_data)
    assertRedirects(response, f'{url_detail_news}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_author_can_delete_comment(
    author_client,
    news,
    url_detail_news,
    url_delete_news,
    comment
):
    initial_comment_count = Comment.objects.filter(news=news).count()
    response = author_client.delete(url_delete_news)
    new_comment_count = Comment.objects.filter(news=news).count()
    assertRedirects(response, f'{url_detail_news}#comments')
    assert new_comment_count == initial_comment_count - 1


def test_user_cant_edit_comment_of_another_user(
    admin_client,
    form_data,
    url_edit_news,
    comment
):
    comment_text = comment.text
    response = admin_client.post(url_edit_news, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_text


def test_user_cant_delete_comment_of_another_user(
    admin_client,
    news,
    url_delete_news,
    comment
):
    initial_comment_count = Comment.objects.filter(news=news).count()
    response = admin_client.delete(url_delete_news)
    new_comment_count = Comment.objects.filter(news=news).count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert new_comment_count == initial_comment_count
