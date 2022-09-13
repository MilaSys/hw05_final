from http import HTTPStatus

from django.shortcuts import reverse
from django.test import Client, TestCase

from ..constants import ALL_COUNT_OF_POSTS
from ..models import HEADER_LENGTH, Group, Post, User


class PostsURLTests(TestCase):
    """Тестирование работоспособности URL адресов"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            "Author", "author@example.com", "qwerty123"
        )
        cls.another_author = User.objects.create_user(
            "Another", "Another@example.com", "qwerty123"
        )
        cls.group = Group.objects.create(
            title="Ж" * HEADER_LENGTH,
            description="Тестовое описание"
        )

        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.auth_another_client = Client()
        cls.auth_another_client.force_login(cls.another_author)

        Post.objects.bulk_create(
            Post(
                text=f"text{i}" * 5,
                author=cls.author,
                group=cls.group
            ) for i in range(ALL_COUNT_OF_POSTS)
        )
        cls.post = Post.objects.latest("id")

        cls.urls_auth_users = (
            (
                "post_create",
                None,
                "/create/",
                "posts/create_post.html",
            ),
            (
                "post_edit",
                (cls.post.id,),
                f"/posts/{cls.post.id}/edit/",
                "posts/create_post.html",
            ),
        )
        cls.urls_no_auth_users = (
            (
                "index", None, "/", "posts/index.html",
            ),
            (
                "group_list",
                (cls.group.slug,),
                f"/group/{cls.group.slug}/",
                "posts/group_list.html"
            ),
            (
                "profile",
                (cls.post.author,),
                f"/profile/{cls.post.author}/",
                "posts/profile.html"
            ),
            (
                "post_detail",
                (cls.post.id,),
                f"/posts/{cls.post.id}/",
                "posts/post_detail.html"
            ),
        )
        cls.url_names = (
            *cls.urls_no_auth_users,
            *cls.urls_auth_users,
        )
        cls.url_comment = (
            "add_comment",
            (cls.post.id,),
            f"/posts/{cls.post.id}/comment/",
            "posts/post_detail.html",
        ),

    def test_urls_uses_correct_namespace(self):
        """URL-адрес использует соответствующий namespace."""
        for namespace, args, address, template in PostsURLTests.url_names:
            with self.subTest(address=address, namespace=namespace, args=args):
                self.assertEqual(
                    address,
                    reverse(f"posts:{namespace}", args=args),
                )

    def test_urls_for_access_at_anonymous_users(self):
        """URL-адрес доступен неавторизованному пользователю."""
        for (
            namespace,
            args,
            address,
            template
        ) in PostsURLTests.urls_no_auth_users:
            with self.subTest(address=address):
                response = PostsURLTests.auth_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_for_access_at_auth_users(self):
        """URL-адрес доступен авторизованному пользователю."""
        for namespace, args, address, template in PostsURLTests.url_names:
            with self.subTest(address=address):
                response = PostsURLTests.auth_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_anonymous_users(self):
        """URL-адрес не доступен анонимному пользователю,
        пользователь будет перенаправлен.
        """
        for (
            namespace,
            args,
            address,
            template
        ) in (*PostsURLTests.urls_auth_users, *PostsURLTests.url_comment):
            with self.subTest(address=address):
                response = self.client.get(address, follow=True)
                self.assertRedirects(
                    response, ("/auth/login/?next=" + address)
                )

    def test_url_edit_for_access_at_author(self):
        """URL-адрес редактирования доступен автору поста."""
        response = PostsURLTests.auth_client.get(
            f"/posts/{PostsURLTests.post.id}/edit/"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_edit_for_access_at_author_but_not_to_author(self):
        """URL-адрес редактирования
        не доступен авторизованному не автору поста.
        """
        response = PostsURLTests.auth_another_client.get(
            f"/posts/{PostsURLTests.post.id}/edit/"
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail", args=[PostsURLTests.post.id])
        )
