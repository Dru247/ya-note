"""Django тесты бизнес логики."""
from http import HTTPStatus

from pytils.translit import slugify

from .fixtures import BaseFixtures
from notes.forms import WARNING
from notes.models import Note


class TestNoteCreation(BaseFixtures):
    """Тесты создания записи."""

    NOTE_TITLE = 'Заголовок записи'
    NOTE_TEXT = 'Текст записи'

    @classmethod
    def setUpTestData(cls):
        """Создание фикстур."""
        super().setUpTestData()
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }

    def test_user_can_create_comment(self):
        """Авторизированный пользователь может создать запись."""
        Note.objects.all().delete()
        response = self.client_reader.post(
            self.url_note_add,
            data=self.form_data
        )
        self.assertRedirects(response, self.url_note_success)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.reader)

    def test_anonymous_user_cant_create_comment(self):
        """Анонимный пользователь не может создать запись."""
        first_notes_count = Note.objects.count()
        self.client.post(self.url_note_add, data=self.form_data)
        second_notes_count = Note.objects.count()
        self.assertEqual(second_notes_count, first_notes_count)


class TestNoteEditDelete(BaseFixtures):
    """Тесты изменения и удаления записи."""

    @classmethod
    def setUpTestData(cls):
        """Тест фикстуры."""
        super().setUpTestData()
        cls.edit_form_data = {
            'title': f'{cls.note.title} new',
            'text': f'{cls.note.text} new',
            'slug': f'{cls.note.slug}_new'
        }

    def test_author_can_delete_note(self):
        """Тест удаление запси автором."""
        first_notes_count = Note.objects.count()
        response = self.client_author.delete(self.url_note_delete)
        self.assertRedirects(response, self.url_note_success)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        second_notes_count = Note.objects.count()
        self.assertEqual(first_notes_count - second_notes_count, 1)

    def test_user_cant_delete_note_of_another_user(self):
        """Тест удаления записи читателем."""
        first_notes_count = Note.objects.count()
        response = self.client_reader.delete(self.url_note_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        second_notes_count = Note.objects.count()
        self.assertEqual(first_notes_count, second_notes_count)

    def test_author_can_edit_note(self):
        """Тест изменения записи автором."""
        response = self.client_author.post(
            self.url_note_edit,
            data=self.edit_form_data
        )
        self.assertRedirects(response, self.url_note_success)
        edit_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(edit_note.title, self.edit_form_data['title'])
        self.assertEqual(edit_note.text, self.edit_form_data['text'])
        self.assertEqual(edit_note.slug, self.edit_form_data['slug'])
        self.assertEqual(edit_note.author, self.note.author)

    def test_user_cant_edit_comment_of_another_user(self):
        """Тест изменения комментария читателем."""
        response = self.client_reader.post(
            self.url_note_edit,
            data=self.edit_form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        edit_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(edit_note.title, self.note.title)
        self.assertEqual(edit_note.text, self.note.text)
        self.assertEqual(edit_note.slug, self.note.slug)
        self.assertEqual(edit_note.author, self.note.author)


class TestNoteSlugCreate(BaseFixtures):
    """Тесты автоматического создания slug."""

    @classmethod
    def setUpTestData(cls):
        """Тест фикстуры."""
        super().setUpTestData()
        cls.form_data = {
            'title': f'{cls.note.title} diff',
            'text': f'{cls.note.text} diff'
        }

    def test_auto_create_slug(self):
        """Тест проверки созданного slug."""
        Note.objects.all().delete()
        self.client_reader.post(self.url_note_add, data=self.form_data)
        note = Note.objects.get()
        self.assertEqual(note.slug, slugify(self.form_data['title']))

    def test_unique_slug(self):
        """Тест проверки уникальности slug."""
        self.form_data['slug'] = self.note.slug
        response = self.client_reader.post(
            self.url_note_add,
            data=self.form_data
        )
        form = response.context['form']
        self.assertFormError(
            form,
            'slug',
            f'{self.note.slug}{WARNING}'
        )
