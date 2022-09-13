from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import path

from . import views
from .constants import (CHANGE_DONE, CHANGE_FORM, LOGGED_OUT, LOGIN,
                              RESET_COMPLETE, RESET_CONFIRM, RESET_DONE,
                              RESET_FORM)

app_name = "users"

urlpatterns = [
    path(
        "signup/",
        views.SignUp.as_view(),
        name="signup",
    ),
    path(
        "login/",
        LoginView.as_view(
            extra_context=LOGIN,
            template_name="users/login.html",
        ),
        name="login",
    ),
    path(
        "logout/",
        LogoutView.as_view(
            extra_context=LOGGED_OUT,
            template_name="users/logged_out.html",
        ),
        name="logout",
    ),
    path(
        "password_change/",
        PasswordChangeView.as_view(
            extra_context=CHANGE_FORM,
            template_name="users/password_change_form.html",
        ),
        name="change_form",
    ),
    path(
        "password_change/done/",
        PasswordChangeDoneView.as_view(
            extra_context=CHANGE_DONE,
            template_name="users/password_change_done.html",
        ),
        name="change_done",
    ),
    path(
        "password_reset/",
        PasswordResetView.as_view(
            extra_context=RESET_FORM,
            template_name="users/password_reset_form.html",
        ),
        name="reset_form",
    ),
    path(
        "password_reset/done/",
        PasswordResetDoneView.as_view(
            extra_context=RESET_DONE,
            template_name="users/password_reset_done.html",
        ),
        name="reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            extra_context=RESET_CONFIRM,
            template_name="users/password_reset_confirm.html",
        ),
        name="reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(
            extra_context=RESET_COMPLETE,
            template_name="users/password_reset_complete.html",
        ),
        name="reset_complete",
    ),
]
