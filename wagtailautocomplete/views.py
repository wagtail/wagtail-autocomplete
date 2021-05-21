from urllib.parse import unquote

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.http import (HttpResponseBadRequest, HttpResponseForbidden,
                         JsonResponse)
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from wagtail import VERSION
from wagtail.contrib.modeladmin.helpers.url import AdminURLHelper
from wagtail.core.models import Page


if VERSION > (2, 0):
    from wagtail.search.backends import get_search_backend
    from wagtail.search.index import Indexed
else:
    from wagtail.wagtailsearch.backends import get_search_backend
    from wagtail.wagtailsearch.index import Indexed


def render_page(page):
    # not actually a page
    if getattr(page, 'specific', None):
        # For support of non-Page models like Snippets.
        page = page.specific
    if callable(getattr(page, 'autocomplete_label', None)):
        title = page.autocomplete_label()
    elif hasattr(page, 'title'):
        title = page.title
    else:
        title = str(page)
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

    results = map(render_page, queryset)
    return JsonResponse(dict(items=list(results)))


@require_GET
def search(request):
    search_query = request.GET.get('query', '')
    target_model = request.GET.get('type', 'wagtailcore.Page')
    try:
        model = apps.get_model(target_model)
    except Exception:
        return HttpResponseBadRequest()

    try:
        limit = int(request.GET.get('limit', 100))
    except ValueError:
        return HttpResponseBadRequest()

    field_name = getattr(model, 'autocomplete_search_field', None)

    if issubclass(model, Indexed):
        search_backend = get_search_backend()
        if field_name:
            queryset = search_backend.search(search_query, model, fields=[field_name])
        else:
            queryset = search_backend.search(search_query, model)
    else:
        field_name = field_name if field_name else 'title'
        filter_kwargs = dict()
        filter_kwargs[field_name + '__icontains'] = search_query
        queryset = model.objects.filter(**filter_kwargs)

    if getattr(queryset, 'live', None):
        # Non-Page models like Snippets won't have a live/published status
        # and thus should not be filtered with a call to `live`.
        queryset = queryset.live()

    exclude = request.GET.get('exclude', '')
    if exclude and queryset:
        try:
            exclusions = [unquote(item) for item in exclude.split(',') if item]
            queryset = queryset.exclude(pk__in=exclusions)
        except: 
            pass
    results = list(map(render_page, queryset[:limit]))

    if request.GET.get('can_edit', False):
        if issubclass(model, Page):
            for index, result in enumerate(results):
                results[index]['edit_link'] = reverse('wagtailadmin_pages:edit', args=(result['pk'],))
        else:
            url_helper = AdminURLHelper(model)
            for index, result in enumerate(results):
                results[index]['edit_link'] = url_helper.get_action_url('edit', result['pk'])

    return JsonResponse(dict(items=results))


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

    instance = method(value)
    return JsonResponse(render_page(instance))
