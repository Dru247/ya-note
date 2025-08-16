"""Фиктуры тестов."""
import pytest

from django.test.client import Client

from notes.models import Note


@pytest.fixture
def author(django_user_model):
    """Создаёт и возвращает пользователя автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Создаёт и возвращает пользователя не автора."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Возвращает клиент авторизированного пользователя автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Возвращает клиент авторизированного пользователя не автора."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def note(author):
    """Создаёт и возвращает экземпляр заметки."""
    note = Note.objects.create(
        title='Заголовок',
        text='Текст заметки',
        slug='note-slug',
        author=author,
    )
    return note


@pytest.fixture
def slug_for_args(note):
    """Возвращает slug заметки для аргумента."""
    return (note.slug,)


@pytest.fixture
def form_data():
    """Возвращает словарь данных для формы заметки."""
    return {
        'title': 'Новый заголовок',
        'text': 'Новый текст',
        'slug': 'new-slug'
    }
