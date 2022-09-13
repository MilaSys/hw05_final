from django.contrib.auth.forms import UserCreationForm
from posts.models import User


class CreationForm(UserCreationForm):
    """Форма регистрации пользователя.

    Attributes:
        first_name - имя
        last_name - фамилия
        username - логин
        email - адрес электронной почты
    """

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
        )
