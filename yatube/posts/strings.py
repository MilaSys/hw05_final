test_models_fields = {
    "Group": {
        "id": {
            "verbose_name": "ID",
            "help_text": "",
        },
        "title": {
            "verbose_name": "Заголовок",
            "help_text": "Придумайте название группы.",
        },
        "slug": {
            "verbose_name": "Короткое название",
            "help_text": "Укажите уникальный адрес для страницы группы. "
                         "Используйте только латиницу, цифры, дефисы "
                         "и знаки подчёркивания",
        },
        "description": {
            "verbose_name": "Описание",
            "help_text": "Опишите чему посвященна группа.",
        },
    },
    "Post": {
        "id": {
            "verbose_name": "ID",
            "help_text": "",
        },
        "text": {
            "verbose_name": "Текст",
            "help_text": "Создайте свой литературный шедевр.",
        },
        "pub_date": {
            "verbose_name": "Дата публикации",
            "help_text": "",
        },
        "author": {
            "verbose_name": "Автор",
            "help_text": "",
        },
        "group": {
            "verbose_name": "Группа",
            "help_text": "Выберите группу",
        },
        "image": {
            "verbose_name": "Изображение",
            "help_text": "Здесь можно загрузить картинку,"
            " объёмом не более 5Мб",
        },
    },
    "Comment": {
        "id": {
            "verbose_name": "ID",
            "help_text": "",
        },
        "post": {
            "verbose_name": "Комментируемый пост",
            "help_text": "",
        },
        "author": {
            "verbose_name": "Автор комментария",
            "help_text": "",
        },
        "text": {
            "verbose_name": "Комментарий",
            "help_text": """Можете оставить здесь своё восхищение,
        конструктивную критику, благодарность.""",
        },
        "pub_date": {
            "verbose_name": "Дата публикации",
            "help_text": "",
        },
    },
}
