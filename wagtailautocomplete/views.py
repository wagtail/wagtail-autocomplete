from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.http import (HttpResponseBadRequest, HttpResponseForbidden,
                         JsonResponse)
from django.views.decorators.http import require_GET, require_POST


def render_page(page):
    if getattr(page, 'specific', None):
        # For support of non-Page models like Snippets.
        page = page.specific
    if callable(getattr(page, 'autocomplete_label', None)):
        title = page.autocomplete_label()
    else:
        title = page.title
    return dict(id=page.id, title=title)


@require_GET
def objects(request):
    ids_param = request.GET.get('ids')
    if not ids_param:
        return HttpResponseBadRequest
    page_type = request.GET.get('type', 'wagtailcore.Page')
    try:
        model = apps.get_model(page_type)
    except Exception:
        return HttpResponseBadRequest

    try:
        ids = [
            int(id)
            for id in ids_param.split(',')
        ]
    except Exception:
        return HttpResponseBadRequest

    queryset = model.objects.filter(id__in=ids)
    if getattr(queryset, 'live', None):
        # Non-Page models like Snippets won't have a live/published status
        # and thus should not be filtered with a call to `live`.
        queryset = queryset.live()

    results = map(render_page, queryset)
    return JsonResponse(dict(items=list(results)))


@require_GET
def search(request):
    search_query = request.GET.get('query', '')
    page_type = request.GET.get('type', 'wagtailcore.Page')
    try:
        model = apps.get_model(page_type)
    except Exception:
        return HttpResponseBadRequest

    field_name = getattr(model, 'autocomplete_search_field', 'title')
    filter_kwargs = dict()
    filter_kwargs[field_name + '__icontains'] = search_query
    queryset = model.objects.filter(**filter_kwargs)
    if getattr(queryset, 'live', None):
        # Non-Page models like Snippets won't have a live/published status
        # and thus should not be filtered with a call to `live`.
        queryset = queryset.live()

    exclude = request.GET.get('exclude', '')
    try:
        exclusions = [int(item) for item in exclude.split(',')]
        queryset = queryset.exclude(pk__in=exclusions)
    except Exception:
        pass

    results = map(render_page, queryset[:20])
    return JsonResponse(dict(items=list(results)))


@require_POST
def create(request, *args, **kwargs):
    value = request.POST.get('value', None)
    if not value:
        return HttpResponseBadRequest

    page_type = request.POST.get('type', 'wagtailcore.Page')
    try:
        model = apps.get_model(page_type)
    except Exception:
        return HttpResponseBadRequest

    content_type = ContentType.objects.get_for_model(model)
    permission_label = '{}.add_{}'.format(
        content_type.app_label,
        content_type.model
    )
    if not request.user.has_perm(permission_label):
        return HttpResponseForbidden

    method = getattr(model, 'autocomplete_create', None)
    if not callable(method):
        return HttpResponseBadRequest

    instance = method(value)
    return JsonResponse(render_page(instance))
