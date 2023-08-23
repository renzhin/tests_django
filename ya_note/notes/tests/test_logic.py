from http import HTTPStatus

from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING

from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):
    NOTE_TITLE = 'Текст заголовка'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'text_zametki'

    @classmethod
    def setUpTestData(cls):
        cls.author1 = User.objects.create(username='Лев Толстой')
        cls.author2 = User.objects.create(username='Клифорд Саймак')
        cls.url = reverse('notes:add')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author1)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }
        cls.note1 = None

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note_for_test = Note.objects.get()
        self.assertEqual(note_for_test.title, self.NOTE_TITLE)
        self.assertEqual(note_for_test.text, self.NOTE_TEXT)
        self.assertEqual(note_for_test.author, self.author1)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def _create_note1(self):
        self.note1 = Note.objects.create(
            title='Тестовый заголовок',
            text='Содержимое заметки',
            slug=self.NOTE_SLUG,
            author=self.author1
        )

    def test_not_unique_slug(self):
        self._create_note1()
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note1.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        self._create_note1()
        url = reverse('notes:edit', args=(self.note1.slug,))
        response = self.auth_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note1.refresh_from_db()
        self.assertEqual(self.note1.title, self.form_data['title'])
        self.assertEqual(self.note1.text, self.form_data['text'])
        self.assertEqual(self.note1.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        self._create_note1()
        url = reverse('notes:edit', args=(self.note1.slug,))
        self.client.force_login(self.author2)
        response = self.client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note1.id)
        self.assertEqual(self.note1.title, note_from_db.title)
        self.assertEqual(self.note1.text, note_from_db.text)
        self.assertEqual(self.note1.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        self._create_note1()
        url = reverse('notes:delete', args=(self.note1.slug,))
        response = self.auth_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        self._create_note1()
        url = reverse('notes:delete', args=(self.note1.slug,))
        self.client.force_login(self.author2)
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
