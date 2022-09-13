from django.contrib import admin

from .models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Настройки отображения таблицы с постами в админ зоне.

    Attributes:
        list_display: "pk", "text", "pub_date", "author", "group"
        - отображаемые поля
        list_editable: "group" - редактируемое поле
        search_fields: "text" - поле для поиска соответствий
        list_filter: "pub_date" - сортируемое поле записей
        empty_value_display: "-пусто-" - заполнитель ячеек со значением None
    """

    list_display = (
        "pk",
        "text",
        "pub_date",
        "author",
        "group",
    )
    list_editable = ("group",)
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Настройки отображения таблицы с постами в админ зоне.

    Attributes:
        list_display: "pk", "title", "slug", "description" - отображаемые поля
        search_fields: "title" - поле для поиска соответствий
        empty_value_display: "-пусто-" - заполнитель ячеек со значением None
    """

    list_display = (
        "pk",
        "title",
        "slug",
        "description",
    )
    search_fields = ("title",)
    empty_value_display = "-пусто-"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Настройки отображения таблицы с комментариями в админ зоне.

    Attributes:
        list_display:
        "pk", "post", "author", "text", "pub_date" - отображаемые поля
    """

    list_display = (
        "pk",
        "post",
        "author",
        "text",
        "pub_date",
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Настройки отображения таблицы с комментариями в админ зоне.

    Attributes:
        list_display:
        "pk", "user", "author", - отображаемые поля
    """

    list_display = (
        "pk",
        "user",
        "author",
    )
