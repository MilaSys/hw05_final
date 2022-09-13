from django.views.generic.base import TemplateView

from .strings import AUTHOR, TECH


class AboutAuthorView(TemplateView):
    """Эссе автора."""

    template_name = "about/author.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author"] = AUTHOR

        return context


class AboutTechView(TemplateView):
    """Владение технологиями"""

    template_name = "about/tech.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tech"] = TECH

        return context
