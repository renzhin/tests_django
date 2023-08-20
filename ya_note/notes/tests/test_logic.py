# news/tests/test_logic.py
from http import HTTPStatus

from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING

# Импортируем из файла с формами список стоп-слов и предупреждение формы.
# Загляните в news/forms.py, разберитесь с их назначением.
from notes.models import Note

User = get_user_model()


class TestNote(TestCase):
    # Текст комментария понадобится в нескольких местах кода,
    # поэтому запишем его в атрибуты класса.
    NOTE_TITLE = 'Текст заголовка'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'text_zametki'

    @classmethod
    def setUpTestData(cls):
        cls.author1 = User.objects.create(username='Лев Толстой')
        cls.author2 = User.objects.create(username='Клифорд Саймак')
        cls.url = reverse('notes:add')
        # Создаём пользователя и клиент, логинимся в клиенте.
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author1)
        # Данные для POST-запроса при создании комментария.
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }

    def test_anonymous_user_cant_create_note(self):
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы с текстом комментария.
        self.client.post(self.url, data=self.form_data)
        # Считаем количество комментариев.
        notes_count = Note.objects.count()
        # Ожидаем, что заметок в базе нет - сравниваем с нулём.
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        # Совершаем запрос через авторизованный клиент.
        response = self.auth_client.post(self.url, data=self.form_data)
        # Проверяем, что редирект привёл к done/.
        self.assertRedirects(response, reverse('notes:success'))
        # Считаем количество заметок.
        notes_count = Note.objects.count()
        # Убеждаемся, что есть одна заметка.
        self.assertEqual(notes_count, 1)
        # Получаем объект заметки  из базы.
        note_for_test = Note.objects.get()
        # Проверяем, что все атрибуты заметки совпадают с ожидаемыми.
        self.assertEqual(note_for_test.title, self.NOTE_TITLE)
        self.assertEqual(note_for_test.text, self.NOTE_TEXT)
        self.assertEqual(note_for_test.author, self.author1)

    def test_not_unique_slug(self):
        self.test_note = Note.objects.create(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            slug=self.NOTE_SLUG,
            author=self.author1
        )
        response = self.auth_client.post(self.url, data=self.form_data)
        # Проверяем, что в ответе содержится ошибка формы для поля slug:
        self.assertFormError(
            response, 'form', 'slug', errors=(self.test_note.slug + WARNING)
        )
        # # Убеждаемся, что количество заметок в базе осталось равным 1:
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        # Убираем поле slug из словаря:
        self.form_data.pop('slug')
        response = self.auth_client.post(self.url, data=self.form_data)
        # Проверяем, что даже без slug заметка была создана:
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        # Получаем созданную заметку из базы:
        new_note = Note.objects.get()
        # Формируем ожидаемый slug:
        expected_slug = slugify(self.form_data['title'])
        # Проверяем, что slug заметки соответствует ожидаемому:
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        self.test_note = Note.objects.create(
            title='1',
            text='1',
            author=self.author1
        )
        url = reverse('notes:edit', args=(self.test_note.slug,))
        response = self.auth_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        # Обновляем объект заметки note: получаем обновлённые данные из БД:
        self.test_note.refresh_from_db()
        self.assertEqual(self.test_note.title, self.form_data['title'])
        self.assertEqual(self.test_note.text, self.form_data['text'])
        self.assertEqual(self.test_note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        self.test_note = Note.objects.create(
            title='1',
            text='1',
            author=self.author1
        )
        url = reverse('notes:edit', args=(self.test_note.slug,))
        self.client.force_login(self.author2)
        response = self.client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Получаем новый объект запросом из БД.
        note_from_db = Note.objects.get(id=self.test_note.id)
        # Проверяем, что атр. объекта из БД равны атрибутам заметки до запроса.
        self.assertEqual(self.test_note.title, note_from_db.title)
        self.assertEqual(self.test_note.text, note_from_db.text)
        self.assertEqual(self.test_note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        self.test_note = Note.objects.create(
            title='1',
            text='1',
            author=self.author1
        )
        url = reverse('notes:delete', args=(self.test_note.slug,))
        response = self.auth_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        self.test_note = Note.objects.create(
            title='1',
            text='1',
            author=self.author1
        )
        url = reverse('notes:delete', args=(self.test_note.slug,))
        self.client.force_login(self.author2)
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
