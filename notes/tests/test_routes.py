"""Django тесты маршрутизации."""
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Тесты маршрутизации."""
    APP_NAME = 'notes'

    @classmethod
    def setUpTestData(cls):
        """Фикстуры класса."""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок записи 1',
            text='Текст записи 1',
            slug='test_slug_1'
        )

    def test_availability_anonymous_client(self):
        """Тест доступа к страницам анонимного пользователя."""
        url_names = (
            ('users:login', None, HTTPStatus.OK),
            ('users:logout', None, HTTPStatus.OK),
            ('users:signup', None, HTTPStatus.OK),
            (self.APP_NAME + ':home', None, HTTPStatus.OK),
            (self.APP_NAME + ':add', None, HTTPStatus.FOUND),
            (self.APP_NAME + ':edit', (self.note.slug,), HTTPStatus.FOUND),
            (self.APP_NAME + ':detail', (self.note.slug,), HTTPStatus.FOUND),
            (self.APP_NAME + ':delete', (self.note.slug,), HTTPStatus.FOUND),
            (self.APP_NAME + ':list', None, HTTPStatus.FOUND),
            (self.APP_NAME + ':success', None, HTTPStatus.FOUND),
        )
        for name, args, status in url_names:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                if name == 'users:logout':
                    response = self.client.post(url)
                else:
                    response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_availability_reader_client(self):
        """Тест доступа к страницам авторизированного пользователя."""
        url_names = (
            ('users:login', None, HTTPStatus.OK),
            ('users:logout', None, HTTPStatus.OK),
            ('users:signup', None, HTTPStatus.OK),
            (self.APP_NAME + ':home', None, HTTPStatus.OK),
            (self.APP_NAME + ':add', None, HTTPStatus.OK),
            (self.APP_NAME + ':edit', (self.note.slug,), HTTPStatus.NOT_FOUND),
            (
                self.APP_NAME + ':detail',
                (self.note.slug,),
                HTTPStatus.NOT_FOUND
            ),
            (
                self.APP_NAME + ':delete',
                (self.note.slug,),
                HTTPStatus.NOT_FOUND
            ),
            (self.APP_NAME + ':list', None, HTTPStatus.OK),
            (self.APP_NAME + ':success', None, HTTPStatus.OK),
        )
        for name, args, status in url_names:
            with self.subTest(name=name):
                self.client.force_login(self.reader)
                url = reverse(name, args=args)
                if name == 'users:logout':
                    response = self.client.post(url)
                else:
                    response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_availability_author_client(self):
        """Тест доступа к страницам авторизированного автора."""
        url_names = (
            (self.APP_NAME + ':edit', (self.note.slug,), HTTPStatus.OK),
            (self.APP_NAME + ':detail', (self.note.slug,), HTTPStatus.OK),
            (self.APP_NAME + ':delete', (self.note.slug,), HTTPStatus.OK)
        )
        for name, args, status in url_names:
            with self.subTest(name=name):
                self.client.force_login(self.author)
                url = reverse(name, args=args)
                if name == 'users:logout':
                    response = self.client.post(url)
                else:
                    response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Тест редиректа анонимного пользователя."""
        login_url = reverse('users:login')
        names = (
            (self.APP_NAME + ':add', None),
            (self.APP_NAME + ':edit', (self.note.slug,)),
            (self.APP_NAME + ':detail', (self.note.slug,)),
            (self.APP_NAME + ':delete', (self.note.slug,)),
            (self.APP_NAME + ':list', None),
            (self.APP_NAME + ':success', None)
        )
        for name, args in names:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
