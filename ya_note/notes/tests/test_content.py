from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    NOTE_TITLE = 'Тестовый заголовок'
    NOTE_TEXT = 'Содержимое заметки'
    USERNAME_AUTHOR = 'Лев Толстой'
    USERNAME_READER = 'Клифорд Саймак'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username=cls.USERNAME_AUTHOR)
        cls.reader = User.objects.create(username=cls.USERNAME_READER)
        cls.note1 = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
        )
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)
        cls.NOTE_LIST_URL = reverse('notes:list')
        cls.NOTE_ADD_URL = reverse('notes:add')
        cls.NOTE_EDIT_URL = reverse('notes:edit', args=(cls.note1.slug,))

    def test_note_in_list_for_different_users(self):
        users_statuses = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for user_client, status in users_statuses:
            response = user_client.get(self.NOTE_LIST_URL)
            object_list = response.context['object_list']
            self.assertIs((self.note1 in object_list), status)
            if status:
                displayed_note = object_list[0]
                self.assertEqual(displayed_note.title, self.note1.title)
                self.assertEqual(displayed_note.text, self.note1.text)
                self.assertEqual(displayed_note.author, self.note1.author)

    def test_note_pages_contains_form(self):
        url_types = (
            (self.NOTE_ADD_URL, None),
            (self.NOTE_EDIT_URL, None),
        )

        for url, slug in url_types:
            response = self.author_client.get(url)
            self.assertIn('form', response.context)
