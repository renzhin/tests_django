from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Анна Петрова')
        cls.note1 = Note.objects.create(
            title='Заметка1',
            text='Текст2',
            author=cls.author,
        )
        cls.HOME_URL = reverse('notes:home')
        cls.LOGIN_URL = reverse('users:login')
        cls.LOGOUT_URL = reverse('users:logout')
        cls.SIGNUP_URL = reverse('users:signup')
        cls.NOTE_LIST_URL = reverse('notes:list')
        cls.NOTE_ADD_URL = reverse('notes:add')
        cls.NOTE_SUCCESS_URL = reverse('notes:success')
        cls.NOTE_DELETE_URL = reverse('notes:delete', args=(cls.note1.slug,))
        cls.NOTE_EDIT_URL = reverse('notes:edit', args=(cls.note1.slug,))
        cls.NOTE_DETAIL_URL = reverse('notes:detail', args=(cls.note1.slug,))

    def test_pages_availability_for_different_users(self):
        users = (self.author, self.reader, None)
        urls = (
            (self.NOTE_LIST_URL, self.reader),
            (self.NOTE_ADD_URL, self.reader),
            (self.NOTE_SUCCESS_URL, self.reader),
            (self.NOTE_DELETE_URL, self.author),
            (self.NOTE_EDIT_URL, self.author),
            (self.NOTE_DETAIL_URL, self.author),
            (self.HOME_URL, None),
            (self.LOGIN_URL, None),
            (self.LOGOUT_URL, None),
            (self.SIGNUP_URL, None),
        )
        for user in users:
            if user:
                self.client.force_login(user)
            for url, access in urls:
                with self.subTest(user=user, url=url, access=access):
                    response = self.client.get(url)
                    if user == self.author:
                        expected_status = HTTPStatus.OK
                    elif user == self.reader and access != self.author:
                        expected_status = HTTPStatus.OK
                    elif user == self.reader and access == self.author:
                        expected_status = HTTPStatus.NOT_FOUND
                    elif user is None and access is None:
                        expected_status = HTTPStatus.OK
                    elif user is None and access in (self.author, self.reader):
                        expected_status = HTTPStatus.FOUND
                    self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            self.NOTE_DELETE_URL,
            self.NOTE_EDIT_URL,
            self.NOTE_DETAIL_URL,
            self.NOTE_LIST_URL,
            self.NOTE_ADD_URL,
            self.NOTE_SUCCESS_URL,
        )
        for name in urls:
            with self.subTest(name=name):
                redirect_url = f'{self.LOGIN_URL}?next={name}'
                response = self.client.get(name)
                self.assertRedirects(response, redirect_url)
