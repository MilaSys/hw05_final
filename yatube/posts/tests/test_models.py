from django.test import Client, TestCase

from ..constants import ALL_COUNT_OF_POSTS, MULTIPLIER_OF_LETTERS
from ..models import COUNT_OF_LETTERS, HEADER_LENGTH, Group, Post, User
from ..strings import test_models_fields


class GeneralTest(TestCase):
    """Тестирование моделей post/group."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            "Author", "author@example.com", "qwerty123"
        )
        cls.group = Group.objects.create(
            title="Ж" * HEADER_LENGTH,
            description="Тестовое описание"
        )

        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)

        Post.objects.bulk_create(
            Post(
                text=f"text{i}" * 5,
                author=cls.author,
                group=cls.group
            ) for i in range(ALL_COUNT_OF_POSTS)
        )
        cls.post = Post.objects.latest("id")

    def _iteration_by_fields(self, box):
        """Итерация по полям форм post/group."""
        for models in [GeneralTest.group, GeneralTest.post]:
            model_name = models._meta.model.__name__
            if str(box) != "help_text":
                fields = [
                    (
                        file.name,
                        file.verbose_name,
                    ) for file in models._meta.fields
                ]
            else:
                fields = [
                    (
                        file.name,
                        file.help_text,
                    ) for file in models._meta.fields
                ]
            for name, value in fields:
                with self.subTest(
                    name=name, value=value, model_name=model_name
                ):
                    test_file = (
                        test_models_fields[model_name][name][box]
                    )
                    error_msg = (
                        f"""Модель !!!{model_name}!!! в поле !!!{name}!!!
                        ожидало значение !!!{box} "{test_file}"!!!
                        """
                    )
                self.assertEqual(test_file, value, error_msg)

    def test_title_label(self):
        """Поля содержат ожидаемый verbose_name."""
        self._iteration_by_fields("verbose_name")

    def test_help_text(self):
        """Поля содержат ожидаемый help_text."""
        self._iteration_by_fields("help_text")

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели "Post" корректно работает __str__."""
        error_msg = f"Вывод не имеет {COUNT_OF_LETTERS} символов"
        self.assertEqual(
            str(GeneralTest.post),
            GeneralTest.post.text[:COUNT_OF_LETTERS],
            error_msg
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели "group" корректно работает __str__."""
        error_msg = f"Вывод не имеет {COUNT_OF_LETTERS} символов"
        self.assertEqual(
            str(GeneralTest.group),
            GeneralTest.group.title,
            error_msg
        )

    def test_text_convert_to_slug(self):
        """Содержимое поля title преобразуется в slug."""
        test_slug = "zh" * MULTIPLIER_OF_LETTERS
        error_msg = f"Вывод ожидал slug '{test_slug}'"
        self.assertEqual(GeneralTest.group.slug, test_slug, error_msg)

    def test_text_slug_max_length_not_exceed(self):
        """Длинный slug обрезается и не превышает
        max_length поля slug в модели.
        """
        max_length_slug = GeneralTest.group._meta.get_field("slug").max_length
        length_slug = len(GeneralTest.group.slug)
        error_msg = f"Вывод ожидает {length_slug} символов"
        self.assertEqual(max_length_slug, length_slug, error_msg)
