from http import HTTPStatus

from django.test import TestCase


class PostsURLTests(TestCase):
    def test_url_not_found(self):
        """Запрос к несуществующему URL-адресу вернёт ошибку 404."""
        response = self.client.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "core/404.html")
