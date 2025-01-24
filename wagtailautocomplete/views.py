from http import HTTPStatus
from urllib.parse import unquote

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import Model, QuerySet
from django.http import (HttpResponseBadRequest, HttpResponseForbidden,
                         HttpResponseNotFound, JsonResponse)
from django.views.decorators.http import require_GET, require_POST


def render_page(page):
    if getattr(page, 'specific', None):
        # For support of non-Page models like Snippets.
        page = page.specific
    if callable(getattr(page, 'autocomplete_label', None)):
        title = page.autocomplete_label()
    else:
        title = page.title
    return dict(pk=page.pk, title=title)


@require_GET
def objects(request):
    pks_param = request.GET.get('pks')
    if not pks_param:
        return HttpResponseBadRequest()
    target_model = request.GET.get('type', 'wagtailcore.Page')
    try:
        model = apps.get_model(target_model)
    except Exception:
        return HttpResponseBadRequest()

    try:
        pks = [
            unquote(pk)
            for pk in pks_param.split(',')
        ]
        queryset = model.objects.filter(pk__in=pks)
    except Exception:
        return HttpResponseBadRequest()

    if getattr(queryset, 'live', None):
        # Non-Page models like Snippets won't have a live/published status
        # and thus should not be filtered with a call to `live`.
        queryset = queryset.live()

    if queryset.count() != len(pks):
        return HttpResponseNotFound('Some objects are either missing or deleted')
    results = map(render_page, queryset)
    return JsonResponse(dict(items=list(results)))


@require_POST
def search(request):
    search_query = request.POST.get('query', '')
    target_model = request.POST.get('type', 'wagtailcore.Page')
    try:
        model = apps.get_model(target_model)
    except Exception:
        return HttpResponseBadRequest()

    try:
        limit = int(request.POST.get('limit', 100))
    except ValueError:
        return HttpResponseBadRequest()

    if callable(getattr(model, 'autocomplete_custom_queryset_filter', None)):
        queryset = model.autocomplete_custom_queryset_filter(search_query)
        validate_queryset(queryset, model)
    else:
        queryset = filter_queryset(search_query, model)

    if getattr(queryset, 'live', None):
        # Non-Page models like Snippets won't have a live/published status
        # and thus should not be filtered with a call to `live`.
        queryset = queryset.live()

    exclude = request.POST.get('exclude', '')
    if exclude:
        exclusions = [unquote(item) for item in exclude.split(',') if item]
        queryset = queryset.exclude(pk__in=exclusions)

    results = map(render_page, queryset[:limit])
    return JsonResponse({"query": search_query, "items": list(results)})


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
    field_name = getattr(model, 'autocomplete_search_field', 'title')
    filter_kwargs = dict()
    filter_kwargs[field_name + '__icontains'] = search_query
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
            'does not return a QuerySet.'
        )

    if queryset.model is not model:
        raise TypeError(
            f'Function "autocomplete_custom_queryset_filter" of model {model}'
            'does not return queryset of {model}.'
        )


@require_POST
def create(request, *args, **kwargs):
    value = request.POST.get('value', None)
    if not value:
        return HttpResponseBadRequest()

    target_model = request.POST.get('type', 'wagtailcore.Page')
    try:
        model = apps.get_model(target_model)
    except Exception:
        return HttpResponseBadRequest()

    content_type = ContentType.objects.get_for_model(model)
    permission_label = '{}.add_{}'.format(
        content_type.app_label,
        content_type.model
    )
    if not request.user.has_perm(permission_label):
        return HttpResponseForbidden()

    method = getattr(model, 'autocomplete_create', None)
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
