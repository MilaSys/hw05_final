from typing import Any, Dict, Type

from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .constants import COUNT_OF_POSTS


def get_page_context(
    queryset: Type[QuerySet], request: HttpRequest
) -> Dict[str, Any]:
    """Возвраящает микс пагинациии и QuerySet модели."""
    paginator = Paginator(queryset, COUNT_OF_POSTS)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return {"page_obj": page_obj, }
