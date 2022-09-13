from django.urls import reverse_lazy
from django.views.generic import CreateView

from .constants import SIGNUP
from .forms import CreationForm


class SignUp(CreateView):
    """Регистрация пользователя."""

    form_class = CreationForm
    success_url = reverse_lazy("posts:index")
    template_name = "users/signup.html"
    extra_context = SIGNUP
