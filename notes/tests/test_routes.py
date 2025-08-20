"""Django тесты маршрутизации."""
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseFixtures(TestCase):
    """Базовые фикстуры."""

    APP_NAME = 'notes'

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
            title='Заголовок записи 1',
            text='Текст записи 1',
            slug='test_slug_1'
        )
        cls.url_user_login = reverse('users:login')
        cls.url_user_logout = reverse('users:logout')
        cls.url_user_signup = reverse('users:signup')
        cls.url_note_home = reverse('users:login')
        cls.url_note_add = reverse(cls.APP_NAME + ':add')
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
        cls.url_note_list = reverse(cls.APP_NAME + ':list')
        cls.url_note_success = reverse(cls.APP_NAME + ':success')


class TestRoutes(BaseFixtures):
    """Тесты маршрутизации."""

    def test_availability_anonymous_client(self):
        """Тест доступа к страницам анонимного пользователя."""
        urls = (
            (self.url_user_login, HTTPStatus.OK),
            (self.url_user_signup, HTTPStatus.OK),
            (self.url_note_home, HTTPStatus.OK),
            (self.url_note_add, HTTPStatus.FOUND),
            (self.url_note_edit, HTTPStatus.FOUND),
            (self.url_note_detail, HTTPStatus.FOUND),
            (self.url_note_delete, HTTPStatus.FOUND),
            (self.url_note_list, HTTPStatus.FOUND),
            (self.url_note_success, HTTPStatus.FOUND)
        )
        for url, status in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_availability_reader_client(self):
        """Тест доступа к страницам авторизированного пользователя."""
        urls = (
            (self.url_user_login, HTTPStatus.OK),
            (self.url_user_signup, HTTPStatus.OK),
            (self.url_note_home, HTTPStatus.OK),
            (self.url_note_add, HTTPStatus.OK),
            (self.url_note_edit, HTTPStatus.NOT_FOUND),
            (self.url_note_detail, HTTPStatus.NOT_FOUND),
            (self.url_note_delete, HTTPStatus.NOT_FOUND),
            (self.url_note_list, HTTPStatus.OK),
            (self.url_note_success, HTTPStatus.OK),
        )
        for url, status in urls:
            with self.subTest(url=url):
                response = self.client_reader.get(url)
                self.assertEqual(response.status_code, status)

    def test_availability_logout_anonymous_and_aut_client(self):
        """Тест доступа logout для анонимного и авторизированного клиента."""
        for client in (self.client, self.client_reader):
            with self.subTest():
                response = client.post(self.url_user_logout)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_author_client(self):
        """Тест доступа к страницам авторизированного автора."""
        urls = (
            (self.url_note_edit, HTTPStatus.OK),
            (self.url_note_detail, HTTPStatus.OK),
            (self.url_note_delete, HTTPStatus.OK)
        )
        for url, status in urls:
            with self.subTest(url=url):
                response = self.client_author.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Тест редиректа анонимного пользователя."""
        urls = (
            self.url_note_add,
            self.url_note_edit,
            self.url_note_detail,
            self.url_note_delete,
            self.url_note_list,
            self.url_note_success
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.url_user_login}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
