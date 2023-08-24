from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author1 = User.objects.create(username='Лев Толстой')
        cls.author2 = User.objects.create(username='Анна Петрова')
        cls.notes1 = Note.objects.create(
            title='Заметка1',
            text='Текст2',
            author=cls.author1,
        )
        cls.HOME_URL = reverse('notes:home')
        cls.LOGIN_URL = reverse('users:login')
        cls.LOGOUT_URL = reverse('users:logout')
        cls.SIGNUP_URL = reverse('users:signup')
        cls.NOTE_LIST_URL = reverse('notes:list')
        cls.NOTE_ADD_URL = reverse('notes:add')
        cls.NOTE_SUCCESS_URL = reverse('notes:success')
        cls.NOTE_DELETE_URL = reverse('notes:delete', args=(cls.notes1.slug,))
        cls.NOTE_EDIT_URL = reverse('notes:edit', args=(cls.notes1.slug,))
        cls.NOTE_DETAIL_URL = reverse('notes:detail', args=(cls.notes1.slug,))

    def test_pages_availability_for_anonymous_client(self):
        urls = (
            self.HOME_URL,
            self.LOGIN_URL,
            self.LOGOUT_URL,
            self.SIGNUP_URL,
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes_modify(self):
        urls = (
            self.NOTE_DELETE_URL,
            self.NOTE_EDIT_URL,
            self.NOTE_DETAIL_URL,
        )
        users_statuses = (
            (self.author1, HTTPStatus.OK),
            (self.author2, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    response = self.client.get(name)
                    self.assertEqual(response.status_code, status)

    def test_availability_for_notes_list_and_success(self):
        urls = (
            self.NOTE_LIST_URL,
            self.NOTE_ADD_URL,
            self.NOTE_SUCCESS_URL,
        )
        users_statuses = (
            (self.author1, HTTPStatus.OK),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    response = self.client.get(name)
                    self.assertEqual(response.status_code, status)

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
