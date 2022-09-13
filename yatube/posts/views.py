from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.cache import cache_page

from .constants import CREATE_POST, EDIT_POST
from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import get_page_context


@cache_page(60 * 20)
def index(request: HttpRequest) -> HttpResponse:
    """Главная страница."""
    template = "posts/index.html"
    context = get_page_context(
        Post.objects.select_related("author", "group"), request
    )

    return render(request, template, context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """Профиль пользователя."""
    template = "posts/profile.html"
    author = get_object_or_404(User, username=username)
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    )
    context = {
        "author": author,
        "following": following
    }
    context.update(
        get_page_context(author.posts.select_related("group"), request)
    )

    return render(request, template, context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """Обзор поста."""
    template = "posts/post_detail.html"
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    comments = post.comments.all()
    context = {
        "post": post,
        "form": form,
        "comments": comments,
    }

    return render(request, template, context)


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """Страница сообщества."""
    template = "posts/group_list.html"
    group = get_object_or_404(Group, slug=slug)
    context = {
        "group": group,
    }
    context.update(
        get_page_context(group.posts.select_related("author"), request)
    )

    return render(request, template, context)


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    """Создание поста."""
    template = "posts/create_post.html"
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == "POST" and form.is_valid():
        post_form = form.save(commit=False)
        post_form.author = request.user
        post_form.save()

        return redirect("posts:profile", username=request.user.username)

    context = {
        "form": form,
    }
    context.update(CREATE_POST)

    return render(request, template, context)


@login_required
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    """Редактирование поста."""
    template = "posts/create_post.html"
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect(reverse("posts:post_detail", args=[post_id]))

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.method == "POST" and form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()

        return redirect(reverse("posts:post_detail", args=[post_id]))

    context = {
        "form": form,
        "post": post,
    }
    context.update(EDIT_POST)

    return render(request, template, context)


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    """Добавить комментарий."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(reverse("posts:post_detail", args=[post_id]))


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    """Страница вывода постов авторов на которых подписан пользователь."""
    template = "posts/follow.html"
    context = get_page_context(
        Post.objects.filter(author__following__user=request.user), request
    )
    return render(request, template, context)


@login_required
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    """Подписаться на интересного автора."""
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect(
        reverse("posts:profile", args=[author])
    )


@login_required
def profile_unfollow(request: HttpRequest, username: str) -> HttpResponse:
    """Отписаться от автора."""
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect(
        reverse("posts:profile", args=[author])
    )
