from http import HTTPStatus

import pytest

from pytest_django.asserts import assertFormError, assertRedirects

from django.urls import reverse

from news.models import Comment

from news.forms import WARNING, BAD_WORDS


def test_user_can_create_comment(author_client, news, author, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assert response.status_code == 302
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_news = Comment.objects.get()
    assert new_news.text == form_data['text']
    assert new_news.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(author_client, news):
    bad_words_data = {
        'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    }
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=bad_words_data)

    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_edit_note(author_client, form_data, news, comment):
    url = reverse('news:edit', args=(news.id,))
    new_url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, form_data)
    assertRedirects(response, f'{new_url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_author_can_delete_comment(author_client, news, comment):
    url = reverse('news:delete', args=(news.id,))
    new_url = reverse('news:detail', args=(news.id,))
    response = author_client.delete(url)
    assertRedirects(response, f'{new_url}#comments')
    assert Comment.objects.count() == 0


def test_user_cant_edit_comment_of_another_user(
    admin_client, form_data, news, comment
):
    comment_text = comment.text
    url = reverse('news:edit', args=(news.id,))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_text


def test_user_cant_delete_comment_of_another_user(admin_client, news, comment):
    url = reverse('news:delete', args=(news.id,))
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
