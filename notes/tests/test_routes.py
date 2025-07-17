from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    APP_NAME = 'notes'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.comment = Note.objects.create(
            author=cls.author,
            title='Заголовок записи 1',
            text='Текст записи 1',
            slug='test_slug_1'
        )

    def test_availability_anonymous_client(self):
        url_names = (
            (self.APP_NAME + ':home', None),
            (self.APP_NAME + ':add', None),
            (self.APP_NAME + ':edit', None),
            (self.APP_NAME + ':detail', None),
            (self.APP_NAME + ':delete', None),
            (self.APP_NAME + ':list', None),
            (self.APP_NAME + ':success', None),
        )
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            for name, args in url_names:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
