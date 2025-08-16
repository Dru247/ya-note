"""Django тесты бизнес логики."""
from http import HTTPStatus

from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    """Тесты создания записи."""
    NOTE_TITLE = 'Заголовок записи'
    NOTE_TEXT = 'Текст записи'
    NOTE_SLUG = slugify(NOTE_TITLE)

    @classmethod
    def setUpTestData(cls):
        """Создание фикстур."""
        cls.url = reverse('notes:add')
        cls.author = User.objects.create(username='Лев Толстой')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT
        }

    def test_user_can_create_comment(self):
        """Авторизированный пользователь может создать запись."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_comment(self):
        """Анонимный пользователь не может создать запись."""
        self.client.post(self.url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)


class TestNoteEditDelete(TestCase):
    """Тесты изменения и удаления записи."""
    NOTE_TITLE = 'Заголовок записи'
    NOTE_TEXT = 'Текст запаиси'
    NEW_NOTE_TEXT = 'Новый текст записи'
    NOTE_SLUG = slugify(NOTE_TITLE)

    @classmethod
    def setUpTestData(cls):
        """Тест фикстуры."""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author
        )
        cls.url_to_redirect = reverse('notes:success')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT
        }

    def test_author_can_delete_note(self):
        """Тест удаление запси автором."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.url_to_redirect)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Тест удаления записи читателем."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Тест изменения записи автором."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.url_to_redirect)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_comment_of_another_user(self):
        """Тест изменения комментария читателем."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)


class TestNoteSlugCreate(TestCase):
    """Тесты автоматического создания slug."""
    NOTE_TITLE = 'Заголовок записи'
    NOTE_TEXT = 'Текст запаиси'

    @classmethod
    def setUpTestData(cls):
        """Тест фикстуры."""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.form_data = {
            'title': 'Следующий заголовок',
            'text': 'Следующий текст'
        }
        cls.url_create = reverse('notes:add')

    def test_auto_create_slug(self):
        """Тест проверки созданного slug."""
        self.assertEqual(self.note.slug, slugify(self.NOTE_TITLE))

    def test_unique_slug(self):
        """Тест проверки уникальности slug."""
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(
            self.url_create,
            data=self.form_data
        )
        form = response.context['form']
        self.assertFormError(
            form,
            'slug',
            self.note.slug + WARNING
        )
