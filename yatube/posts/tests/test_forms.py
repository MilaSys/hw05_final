import shutil
import tempfile
from xml.etree.ElementTree import Comment

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..constants import ALL_COUNT_OF_POSTS
from ..models import HEADER_LENGTH, Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormTests(TestCase):
    """Тестирование форм приложения posts."""

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
        cls.another_group = Group.objects.create(
            title="Другой тест",
            description="Другое тестовое описание"
        )

        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        Post.objects.bulk_create(
            Post(
                text=f"text{i}" * 5,
                author=cls.author,
                group=cls.group,

            ) for i in range(ALL_COUNT_OF_POSTS)
        )
        cls.post = Post.objects.latest("id")

        cls.form_data = {
            "text": "Тестовый текст",
            "group": cls.group.id,
            "image": uploaded,
        }
        cls.expected_form_data = {
            "text": "Тестовый текст",
            "group": cls.group.id,
            "image": "posts/small.gif",
        }
        cls.edit_form_data = {
            "text": "Изменённый тестовый текст",
            "group": cls.another_group.id,
        }
        cls.add_comment_data = {
            "text": "Тестовый комментарий",
        }
        cls.form_error = (
            (
                {
                    "text": "",
                    "group": cls.group.id,
                },
                (
                    "form",
                    "text",
                    "Обязательное поле.",
                ),
            ),
            (
                {
                    "text": "mm",
                    "group": cls.group.id,
                },
                (
                    "form",
                    "text",
                    "Напишите что-то более осмысленное.",
                ),
            ),
            (
                {
                    "text": "ддддллллллл",
                    "group": cls.group.id,
                },
                (
                    "form",
                    "text",
                    "Напишите что-то более осмысленное.",
                ),
            )
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Форма добавления поста работает корректно."""
        posts = Post.objects.values_list("id", flat=True)
        count_post_before = len(posts)
        FormTests.auth_client.post(
            reverse("posts:post_create"),
            data=FormTests.form_data,
            follow=True
        )
        create_post = Post.objects.exclude(pk__in=list(posts))
        self.assertEqual(
            create_post.count(), 1
        )
        self.assertEqual(
            Post.objects.count(), count_post_before + 1
        )
        self.assertEqual(
            FormTests.expected_form_data,
            *create_post.values("text", "group", "image")
        )

    def test_adding_correct_data(self):
        """Валидация добавления/изменения поста работает корректно."""
        post_count = Post.objects.count()
        for form_data, validation in FormTests.form_error:
            response = FormTests.auth_client.post(
                reverse("posts:post_create"),
                data=form_data,
                follow=True
            )
            self.assertEqual(Post.objects.count(), post_count)
            with self.subTest(form_data=form_data, validation=validation):
                self.assertFormError(response, *validation)

    def test_edit_post(self):
        """Форма редактирования поста работает корректно."""
        post_count = Post.objects.count()
        response = FormTests.auth_client.post(
            reverse("posts:post_edit", args=[FormTests.post.pk]),
            data=FormTests.edit_form_data,
            follow=True
        )
        edit_post = Post.objects.filter(pk=FormTests.post.pk)
        self.assertRedirects(
            response,
            reverse("posts:post_detail", args=[FormTests.post.pk])
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(
            FormTests.edit_form_data,
            *edit_post.values("text", "group")
        )

    def test_add_comment(self):
        """Форма добавления комментария к посту работает корректно."""
        post_count = Post.objects.count()
        FormTests.auth_client.post(
            reverse("posts:add_comment", args=[FormTests.post.pk]),
            data=FormTests.add_comment_data,
            follow=True
        )
        response = FormTests.auth_client.get(
            reverse("posts:post_detail", args=[FormTests.post.pk])
        )
        comment_post = Comment.objects.filter(post=FormTests.post.pk)
        self.assertEqual(Post.objects.count(), post_count)

        self.assertEqual(
            FormTests.add_comment_data,
            *comment_post.values("text")
        )
        self.assertContains(response, "Тестовый комментарий")
