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

    def test_note_in_list_for_different_users(self):
        users_statuses = (
            (self.author1, True),
            (self.author2, False),
        )
        for user, status in users_statuses:
            url = reverse('notes:list')
            self.client.force_login(user)
            response = self.client.get(url)
            object_list = response.context['object_list']
            self.assertIs((self.notes1 in object_list), status)

    def test_note_pages_contains_form(self):
        urls_types = (
            ('notes:add', None),
            ('notes:edit', (self.notes1.slug,)),
        )
        for url_, slug_ in urls_types:
            url = reverse(url_, args=(slug_))
            self.client.force_login(self.author1)
            response = self.client.get(url)
            self.assertIn('form', response.context)
