from django.db import models


class PubDateModel(models.Model):
    """Абстрактная модель.

    Attributes:
        pub_date: DateTimeField - дата публикации
    """

    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True
    )

    class Meta:
        abstract = True
