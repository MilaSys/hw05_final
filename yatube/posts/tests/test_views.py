import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..constants import ALL_COUNT_OF_POSTS, FIRST_PAGE_POSTS, NEXT_PAGE_POSTS
from ..models import HEADER_LENGTH, Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    """Тестирование приложения posts модуль views."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            "Author", "author@example.com", "qwerty123"
        )
        cls.another_author = User.objects.create_user(
            "Another", "Another@example.com", "qwerty123"
        )
        cls.follower = User.objects.create_user(
            "Follower", "Follower@example.com", "qwerty123"
        )
        cls.group = Group.objects.create(
            title="Ж" * HEADER_LENGTH,
            description="Тестовое описание"
        )
        cls.another_group = Group.objects.create(
            title="Другой тест",
            description="Другое тестовое описание"
        )

        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.auth_another_client = Client()
        cls.auth_another_client.force_login(cls.another_author)
        cls.auth_follower_client = Client()
        cls.auth_follower_client.force_login(cls.follower)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        Post.objects.bulk_create(
            Post(
                text=f"text{i}" * 5,
                author=cls.author,
                group=cls.group,
                image=cls.uploaded
            ) for i in range(ALL_COUNT_OF_POSTS)
        )
        cls.post = Post.objects.latest("id")
        cache.clear()

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

    def setUp(self):
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует корректный шаблон."""
        for namespace, args, address, template in PostsPagesTests.url_names:
            with self.subTest(
                namespace=namespace, args=args, template=template
            ):
                response = PostsPagesTests.auth_client.get(
                    reverse(f"posts:{namespace}", args=args)
                )
                self.assertTemplateUsed(response, template)

    def test_page_show_last_post(self):
        """Шаблон index/group_list/profile/post_detail
        принимает пост созданный последним и выводит его первым в выдаче.
        """
        for (
            namespace, args, address, template
        ) in PostsPagesTests.urls_no_auth_users:
            with self.subTest(
                namespace=namespace, args=args, template=template
            ):
                response = PostsPagesTests.auth_client.get(
                    reverse(f"posts:{namespace}", args=args)
                )
                if namespace == "post_detail":
                    context = response.context["post"]
                else:
                    context = response.context["page_obj"][0]
                self.assertEqual(
                    context, PostsPagesTests.post
                )

    def test_group_list_page_not_show_post_another_group(self):
        """На странице группы не отображается пост принадлежащий другой группе.
        """
        response = PostsPagesTests.auth_client.get(
            reverse(
                "posts:group_list", args=[PostsPagesTests.another_group.slug]
            )
        )
        self.assertNotIn(PostsPagesTests.post, response.context["page_obj"])

    def test_profile_page_not_show_post_another_author(self):
        """На странице автора не отображается
        пост принадлежащий другому автору.
        """
        response = PostsPagesTests.auth_client.get(
            reverse("posts:profile", args=[PostsPagesTests.another_author])
        )
        self.assertNotIn(PostsPagesTests.post, response.context["page_obj"])

    def _assert_post_has_attrs(self, post_object):
        """Макет проверки контекста
        для шаблонов index/group_list/profile/post_detail/post_edit.
        """
        self.assertEqual(
            post_object.id,
            PostsPagesTests.post.pk
        )
        self.assertEqual(
            post_object.text,
            PostsPagesTests.post.text
        )
        self.assertEqual(
            post_object.author,
            PostsPagesTests.author
        )
        self.assertEqual(
            post_object.group,
            PostsPagesTests.group
        )
        self.assertEqual(
            post_object.image,
            PostsPagesTests.post.image
        )

    def test_index_page_show_correct_context(self):
        """Проверяем контекст шаблона index."""
        response = PostsPagesTests.auth_client.get(reverse("posts:index"))
        self._assert_post_has_attrs(response.context["page_obj"][0])

    def test_group_list_page_show_correct_context(self):
        """Проверяем контекст шаблона group_list."""
        response = PostsPagesTests.auth_client.get(
            reverse("posts:group_list", args=[PostsPagesTests.group.slug])
        )
        self.assertEqual(
            response.context["group"],
            PostsPagesTests.group
        )
        self._assert_post_has_attrs(response.context["page_obj"][0])

    def test_profile_show_correct_context(self):
        """Проверяем контекст шаблона profile."""
        response = PostsPagesTests.auth_client.get(
            reverse("posts:profile", args=[PostsPagesTests.author])
        )
        self.assertEqual(
            response.context["author"],
            PostsPagesTests.author
        )
        self._assert_post_has_attrs(response.context["page_obj"][0])

    def test_post_detail_show_correct_context(self):
        """Проверяем контекст шаблона post_detai."""
        response = PostsPagesTests.auth_client.get(
            reverse(
                "posts:post_detail", args=[PostsPagesTests.post.pk]
            )
        )
        self._assert_post_has_attrs(response.context["post"])

    def assert_post_response(self, response):
        """Макет проверки шаблонов post_create/post_edit."""
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value, expected=expected):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_show_correct_context(self):
        """Проверяем контекст шаблона post_create."""
        response = PostsPagesTests.auth_client.get(
            reverse("posts:post_create")
        )
        self.assert_post_response(response)

    def test_post_edit_page_show_correct_context(self):
        """Проверяем контекст шаблона post_edit."""
        response = PostsPagesTests.auth_client.get(
            reverse(
                "posts:post_edit", args=[PostsPagesTests.post.pk]
            )
        )
        self._assert_post_has_attrs(response.context["post"])
        self.assert_post_response(response)

    def test_index_cache(self):
        """Проверяем кеширование страницы index."""
        response = PostsPagesTests.auth_client.get(reverse("posts:index"))
        PostsPagesTests.auth_client.post(
            reverse("posts:post_create"),
            data={"text": "Проверка кэша", },
            follow=True
        )
        response = PostsPagesTests.auth_client.get(reverse("posts:index"))
        self.assertNotContains(response, "Проверка кэша")
        cache.clear()
        response = PostsPagesTests.auth_client.get(reverse("posts:index"))
        self.assertContains(response, "Проверка кэша")

    def test_follow(self):
        """Проверяем возможность подписки на автора."""
        follower_list = Follow.objects.values_list("id", flat=True)
        count_follower_before = len(follower_list)
        self.auth_follower_client.get(
            reverse(
                "posts:profile_follow",
                args=[PostsPagesTests.author]
            )
        )
        create_follower = Follow.objects.exclude(pk__in=list(follower_list))
        self.assertEqual(create_follower.count(), 1)
        self.assertEqual(Follow.objects.count(), count_follower_before + 1)

    def test_unfollow(self):
        """Проверяем возможность отписки от автора."""
        self.auth_follower_client.get(
            reverse(
                "posts:profile_follow",
                args=[PostsPagesTests.author]
            )
        )
        follower_list = Follow.objects.values_list("id", flat=True)
        count_follower_before = len(follower_list)
        self.auth_follower_client.get(
            reverse(
                "posts:profile_unfollow",
                args=[PostsPagesTests.author]
            )
        )
        self.assertEqual(Follow.objects.count(), count_follower_before - 1)

    def test_follow_page_show_follower_no_not_other_follower(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан.
        """
        self.auth_follower_client.get(
            reverse(
                "posts:profile_follow",
                args=[PostsPagesTests.author]
            )
        )
        self.assertEqual(Follow.objects.count(), 1)
        self.auth_client.post(
            reverse(
                "posts:post_create"
            ),
            data={"text": "Тестовый текст"},
            follow=True
        )
        response = self.auth_follower_client.get(reverse("posts:follow_index"))
        self.assertContains(response, "Тестовый текст")
        response = self.auth_another_client.get(
            reverse("posts:follow_index")
        )
        self.assertNotContains(response, "Тестовый текст")


class PaginatorsTest(TestCase):
    """Тестируем пагинацию."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            "Author", "author@example.com", "qwerty123"
        )
        cls.group = Group.objects.create(
            title="Тест",
            description="Тестовое описание"
        )
        posts = (
            Post(
                text=f"text{i}",
                author=cls.author,
                group=cls.group
            ) for i in range(ALL_COUNT_OF_POSTS)
        )
        Post.objects.bulk_create(posts)

        cls.url_names = (
            ("index", None),
            ("group_list", (cls.group.slug,)),
            ("profile", (cls.author,)),
        )

    def _test_pagination(self, url_params, expected_count):
        """Макет проверки работы пагинатора."""
        for reverse_name, args in PaginatorsTest.url_names:
            with self.subTest(reverse_name=reverse_name, args=args):
                response = self.client.get(
                    reverse(f"posts:{reverse_name}", args=args) + url_params
                )
                self.assertEqual(
                    len(response.context["page_obj"]), expected_count
                )

    def test_first_page_contains_ten_records(self):
        """Тестируем работу пагинатора на первой странице."""
        self._test_pagination("", FIRST_PAGE_POSTS)

    def test_second_page_contains_three_records(self):
        """Тестируем работу пагинатора на второй странице."""
        self._test_pagination("?page=2", NEXT_PAGE_POSTS)
