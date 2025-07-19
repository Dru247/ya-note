"""Django тесты контента."""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    """Тесты контента."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Заголовок записи',
            text='Текст записи',
            author=cls.author
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.url_create = reverse('notes:add')
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_note_list = reverse('notes:list')

    def test_notes_list_auth_author_user(self):
        """Проверка отображения записей для автора."""
        response = self.author_client.get(self.url_note_list)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)

    def test_notes_list_reader_user(self):
        """Проверка отображения записей для не автора."""
        response = self.reader_client.get(self.url_note_list)
        notes = response.context['object_list']
        self.assertNotIn(self.note, notes)

    def test_contains_form_in_pages(self):
        """Тест наличия формы на страницах создания и изменения записи."""
        for url in (self.url_create, self.url_edit):
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
