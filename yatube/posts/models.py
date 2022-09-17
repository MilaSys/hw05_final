from django.contrib.auth import get_user_model
from django.db import models
from pytils.translit import slugify

from core.models import PubDateModel
from posts.constants import COUNT_OF_LETTERS, HEADER_LENGTH

User = get_user_model()


class Group(models.Model):
    """Модель таблицы сообществ.

    Attributes:
        title: CharField - название сообщества
        slug: SlugField - краткое название сообщества используемое в адресной
        строке
        description: TextField - описание сообщества
    """

    title = models.CharField(
        max_length=HEADER_LENGTH,
        verbose_name="Заголовок",
        help_text="Придумайте название группы.",
    )
    slug = models.SlugField(
        unique=True,
        max_length=HEADER_LENGTH,
        verbose_name="Короткое название",
        help_text=(
            "Укажите уникальный адрес для страницы группы. "
            "Используйте только латиницу, цифры, дефисы "
            "и знаки подчёркивания"
        ),
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Опишите чему посвященна группа.",
    )

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:HEADER_LENGTH]
        super().save(*args, **kwargs)


class Post(PubDateModel, models.Model):
    """Модель таблицы с постами.

    Attributes:
        text: TextField - текст поста
        pub_date: DateTimeField - дата публикации
        author: ForeignKey - ссылка (ID) на объект класса User
        group: ForeignKey - ссылка (ID) на объект класса Group
        image: ImageField - изображение загруженное автором
    """

    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="posts",
    )
    group = models.ForeignKey(
        Group,
        verbose_name="Группа",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts",
        help_text="Выберите группу",
    )
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="posts/",
        blank=True,
        help_text="Здесь можно загрузить картинку, объёмом не более 5Мб",
    )

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ("-pub_date", "-id",)

    def __str__(self) -> str:
        return self.text[:COUNT_OF_LETTERS]


class Comment(PubDateModel, models.Model):
    """Модель таблицы комментариев.

    Attributes:
        post: ForeignKey - ссылка (ID) на объект класса Post
        author: ForeignKey - ссылка (ID) на объект класса User
        text: TextField - комментарий
        pub_date: DateTimeField - дата публикации.
    """
    post = models.ForeignKey(
        Post,
        verbose_name="Комментируемый пост",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор комментария",
        on_delete=models.CASCADE,
        related_name="comments",
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.text[:COUNT_OF_LETTERS]


class Follow(models.Model):
    """Модель таблицы подписчиков.

    Attributes:
        user: ForeignKey - ссылка (ID) на объект класса User
        author: ForeignKey - ссылка (ID) на объект класса User
    """
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="following",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ("-id",)
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_follow"
            )
        ]
