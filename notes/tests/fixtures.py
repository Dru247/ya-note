"""Фикстуры тестов."""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseFixtures(TestCase):
    """Базовые фикстуры."""

    APP_NAME = 'notes'
    NOTE_TITLE = 'Заголовок записи'
    NOTE_TEXT = 'Текст записи'
    NOTE_SLUG = 'slug_note'

    @classmethod
    def setUpTestData(cls):
        """Фикстуры класса."""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.client_author = Client()
        cls.client_author.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.client_reader = Client()
        cls.client_reader.force_login(cls.reader)
        cls.note = Note.objects.create(
            author=cls.author,
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG
        )
        cls.url_user_login = reverse('users:login')
        cls.url_user_logout = reverse('users:logout')
        cls.url_user_signup = reverse('users:signup')
        cls.url_note_home = reverse('users:login')
        cls.url_note_add = reverse(cls.APP_NAME + ':add')
        cls.url_note_list = reverse(cls.APP_NAME + ':list')
        cls.url_note_success = reverse(cls.APP_NAME + ':success')
        cls.url_note_edit = reverse(
            cls.APP_NAME + ':edit',
            args=(cls.note.slug,)
        )
        cls.url_note_detail = reverse(
            cls.APP_NAME + ':detail',
            args=(cls.note.slug,)
        )
        cls.url_note_delete = reverse(
            cls.APP_NAME + ':delete',
            args=(cls.note.slug,)
        )
