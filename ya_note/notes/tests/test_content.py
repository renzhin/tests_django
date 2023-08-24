from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author1 = User.objects.create(username='Лев Толстой')
        cls.author2 = User.objects.create(username='Анна Петрова')
        cls.notes1 = Note.objects.create(
            title='Заметка1',
            text='Текст2',
            author=cls.author1,
        )
        cls.NOTE_LIST_URL = reverse('notes:list')
        cls.NOTE_ADD_URL = reverse('notes:add')
        cls.NOTE_EDIT_URL = reverse('notes:edit', args=(cls.notes1.slug,))

    def login_user(self, user):
        self.client.force_login(user)

    def test_note_in_list_for_different_users(self):
        users_statuses = (
            (self.author1, True),
            (self.author2, False),
        )
        for user, status in users_statuses:
            self.login_user(user)
            response = self.client.get(self.NOTE_LIST_URL)
            object_list = response.context['object_list']
            self.assertIs((self.notes1 in object_list), status)
            if status:
                displayed_note = object_list[0]
                self.assertEqual(displayed_note.title, self.notes1.title)
                self.assertEqual(displayed_note.text, self.notes1.text)
                self.assertEqual(displayed_note.author, self.notes1.author)

    def test_note_pages_contains_form(self):
        url_types = (
            (self.NOTE_ADD_URL, None),
            (self.NOTE_EDIT_URL, None),
        )

        for url, slug in url_types:
            self.login_user(self.author1)
            response = self.client.get(url)
            self.assertIn('form', response.context)
