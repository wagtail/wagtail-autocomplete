"""Allow rules for use with ``WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS``.

Each rule takes ``(queryset, request)`` and returns the subset of the queryset
that the request is allowed to see.
"""

from collections.abc import Callable

from django.db.models import QuerySet
from django.http import HttpRequest
from wagtail.models import CollectionViewRestriction, PageViewRestriction

AllowRule = Callable[[QuerySet, HttpRequest], QuerySet]


def live_pages(queryset: QuerySet, request: HttpRequest) -> QuerySet:
    """Exclude draft pages. Also applied to pages in the admin endpoints."""
    return queryset.live()


def viewable_pages(queryset: QuerySet, request: HttpRequest) -> QuerySet:
    """Exclude pages behind a view restriction that the request does not
    satisfy (private pages and their descendants)."""
    for restriction in PageViewRestriction.objects.select_related("page"):
        if not restriction.accept_request(request):
            queryset = queryset.not_descendant_of(restriction.page, inclusive=True)
    return queryset


def viewable_documents(queryset: QuerySet, request: HttpRequest) -> QuerySet:
    """Exclude documents in collections behind a view restriction that the
    request does not satisfy (including descendant collections)."""
    for restriction in CollectionViewRestriction.objects.select_related("collection"):
        if not restriction.accept_request(request):
            queryset = queryset.exclude(
                collection__in=restriction.collection.get_descendants(inclusive=True)
            )
    return queryset
