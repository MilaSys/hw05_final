from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма изменения/добавления поста.

    Atributes:
        text: TextField - текст поста, обязательно для заполнения
        group: ForeignKey - ссылка (ID) на объект класса Group, не обязательно
                            для заполнения
        image: ImageField - изображение загружаемое автором поста,
                            не обязательно для заполнения
    """

    class Meta:
        model = Post
        fields = ("text", "group", "image",)

    def clean_text(self) -> str:
        """Проверка на содержание текста"""
        text_check = self.cleaned_data["text"]
        if text_check == "" or text_check.isspace():
            raise forms.ValidationError("Заполните поле поста текстом.")

        if len(set(text_check)) < 3:
            raise forms.ValidationError("Напишите что-то более осмысленное.")

        return text_check


class CommentForm(forms.ModelForm):
    """Форма добавления комментария.

    Atributes:
        text: TextField - текст комментария, обязательно для заполнения
    """
    class Meta:
        model = Comment
        fields = ("text",)
