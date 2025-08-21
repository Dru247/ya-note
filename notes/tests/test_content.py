"""Django тесты контента."""
from .fixtures import BaseFixtures
from notes.forms import NoteForm


class TestContent(BaseFixtures):
    """Тесты контента."""

    def test_notes_list_auth_author_user(self):
        """Проверка отображения записей для автора."""
        response = self.client_author.get(self.url_note_list)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)

    def test_notes_list_reader_user(self):
        """Проверка отображения записей для не автора."""
        response = self.client_reader.get(self.url_note_list)
        notes = response.context['object_list']
        self.assertNotIn(self.note, notes)

    def test_contains_form_in_pages(self):
        """Тест наличия формы на страницах создания и изменения записи."""
        for url in (self.url_note_add, self.url_note_edit):
            with self.subTest(url=url):
                response = self.client_author.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
