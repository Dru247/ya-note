"""Django тесты маршрутизации."""
from http import HTTPStatus

from .fixtures import BaseFixtures


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
        for client, name_client in (
            (self.client, 'анонимный клиент'),
            (self.client_reader, 'клиент автора')
        ):
            with self.subTest(client=name_client):
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
