from http import HTTPStatus
from urllib.parse import unquote

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import connections, router
from django.db.models import IntegerField, Model, QuerySet
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotFound,
    JsonResponse,
)
from django.views.decorators.http import require_GET, require_POST


def render_page(page):
    if getattr(page, "specific", None):
        # For support of non-Page models like Snippets.
        page = page.specific
    if callable(getattr(page, "autocomplete_label", None)):
        title = page.autocomplete_label()
    else:
        title = page.title
    return {"pk": page.pk, "title": title}


def integer_range(model, internal_type):
    """
    Return the smallest and largest integers the model's database accepts for
    the given field type.
    """
    connection = connections[router.db_for_read(model)]
    low, high = connection.ops.integer_field_range(internal_type)
    # Django < 5.0 reports no range for SQLite, which still can't handle
    # integers outside 64 bits.
    if low is None:
        low = -(2**63)
    if high is None:
        high = 2**63 - 1
    return low, high


def clean_pks(model, values):
    """
    Convert primary keys from a request with the model's primary key field,
    so invalid or out of range values fail before reaching the database.

    Raises:
        ValidationError, TypeError, ValueError: Raised if a value isn't a
            valid primary key. Built-in fields raise ValidationError, but
            custom fields may raise the others.
    """
    field = model._meta.pk
    # A multi-table inherited model's primary key, such as page_ptr on Page
    # subclasses, links to its parent's.
    while field.is_relation:
        field = field.target_field

    pks = [field.to_python(unquote(value)) for value in values]
    if None in pks:
        raise ValidationError("Primary keys can't be empty.")
    if isinstance(field, IntegerField):
        low, high = integer_range(model, field.get_internal_type())
        if not all(low <= pk <= high for pk in pks):
            raise ValidationError("Primary key out of range.")
    return pks


@require_GET
def objects(request):
    pks_param = request.GET.get("pks")
    if not pks_param:
        return HttpResponseBadRequest()
    target_model = request.GET.get("type", "wagtailcore.Page")
    try:
        model = apps.get_model(target_model)
    except (LookupError, ValueError):
        return HttpResponseBadRequest()

    try:
        pks = clean_pks(model, pks_param.split(","))
    except (TypeError, ValueError, ValidationError):
        return HttpResponseBadRequest()

    queryset = model.objects.filter(pk__in=pks)

    if getattr(queryset, "live", None):
        # Non-Page models like Snippets won't have a live/published status
        # and thus should not be filtered with a call to `live`.
        queryset = queryset.live()

    if queryset.count() != len(pks):
        return HttpResponseNotFound("Some objects are either missing or deleted")
    results = map(render_page, queryset)
    return JsonResponse({"items": list(results)})


@require_POST
def search(request):
    search_query = request.POST.get("query", "")
    target_model = request.POST.get("type", "wagtailcore.Page")
    try:
        model = apps.get_model(target_model)
    except (LookupError, ValueError):
        return HttpResponseBadRequest()

    try:
        limit = int(request.POST.get("limit", 100))
    except ValueError:
        return HttpResponseBadRequest()
    # Querysets can't be sliced with a negative number, and databases reject
    # a LIMIT above their largest integer.
    if not 0 <= limit <= integer_range(model, "BigIntegerField")[1]:
        return HttpResponseBadRequest()

    if callable(getattr(model, "autocomplete_custom_queryset_filter", None)):
        queryset = model.autocomplete_custom_queryset_filter(
            search_query, request=request
        )
        validate_queryset(queryset, model)
    else:
        queryset = filter_queryset(search_query, model)

        if getattr(queryset, "live", None):
            # Non-Page models like Snippets won't have a live/published status
            # and thus should not be filtered with a call to `live`.
            queryset = queryset.live()

    exclude = request.POST.get("exclude", "")
    if exclude:
        try:
            exclusions = clean_pks(model, [item for item in exclude.split(",") if item])
        except (TypeError, ValueError, ValidationError):
            return HttpResponseBadRequest()
        queryset = queryset.exclude(pk__in=exclusions)

    results = map(render_page, queryset[:limit])
    return JsonResponse({"items": list(results)})


def filter_queryset(search_query: str, model: Model) -> QuerySet:
    """
    Filter db entries of the given model for the given search_query and
    returns it. The filter operates on either the default column title or the
    custom column defined in autocomplete_search_field.

    Args:
        search_query (str): Term to search for.
        model (Model): Model to search in.

    Returns:
        QuerySet: QuerySet containing the search results.
    """
    field_name = getattr(model, "autocomplete_search_field", "title")
    filter_kwargs = {}
    filter_kwargs[field_name + "__icontains"] = search_query
    return model.objects.filter(**filter_kwargs)


def validate_queryset(queryset: QuerySet, model: Model):
    """
    Validate that a given QuerySet is of type QuerySet and refers to the given
    model.

    Args:
        queryset (QuerySet): QuerySet to validate.
        model (Model): Expected django model class.

    Raises:
        TypeError: Raised if given QuerySet is not of type QuerySet
        TypeError: Raised if given QuerySet refers to a different model than
            expected.
    """
    if not isinstance(queryset, QuerySet):
        raise TypeError(
            f'Function "autocomplete_custom_queryset_filter" of model {model}'
            "does not return a QuerySet."
        )

    if queryset.model is not model:
        raise TypeError(
            f'Function "autocomplete_custom_queryset_filter" of model {model}'
            "does not return queryset of {model}."
        )


@require_POST
def create(request, *args, **kwargs):
    value = request.POST.get("value", None)
    if not value:
        return HttpResponseBadRequest()

    target_model = request.POST.get("type", "wagtailcore.Page")
    try:
        model = apps.get_model(target_model)
    except (LookupError, ValueError):
        return HttpResponseBadRequest()

    content_type = ContentType.objects.get_for_model(model)
    permission_label = f"{content_type.app_label}.add_{content_type.model}"
    if not request.user.has_perm(permission_label):
        return HttpResponseForbidden()

    method = getattr(model, "autocomplete_create", None)
    if not callable(method):
        return HttpResponseBadRequest()

    try:
        instance = method(value)
    except ValidationError as e:
        return JsonResponse(
            data=getattr(e, "message_dict", {"detail": "Invalid input."}),
            status=HTTPStatus.BAD_REQUEST,
        )

    return JsonResponse(render_page(instance))
