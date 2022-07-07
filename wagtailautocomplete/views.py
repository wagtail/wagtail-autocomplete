from urllib.parse import unquote

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
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


@require_GET
def search(request):
    search_query = request.GET.get('query', '')
    target_model = request.GET.get('type', 'wagtailcore.Page')
    try:
        target_model = apps.get_model(target_model)
    except Exception:
        return HttpResponseBadRequest()

    try:
        limit = int(request.GET.get('limit', 100))
    except ValueError:
        return HttpResponseBadRequest()

    field_name = getattr(target_model, 'autocomplete_search_field', 'title')
    filter_kwargs = dict()
    filter_kwargs[field_name + '__icontains'] = search_query
    queryset = target_model.objects.filter(**filter_kwargs)

    if getattr(queryset, 'live', None):
        # Non-Page models like Snippets won't have a live/published status
        # and thus should not be filtered with a call to `live`.
        queryset = queryset.live()

    # Get exclusions based on the existing instance.
    instance = request.GET.get('instance', '')
    db_field = request.GET.get('db_field', '')
    if instance and db_field:
        model_str, field_str = db_field.rsplit(".", 1)

        try:
            model = apps.get_model(model_str)
        except Exception:
            return HttpResponseBadRequest("The model '%s' could not be found." % model_str)

        model_field = model._meta.get_field(field_str)
        model_instance = model.objects.get(pk=instance)
        instance_field = getattr(model_instance, field_str)

        if model_field.many_to_many:
            # Get all existing pks as exclusions
            exclusions = instance_field.all().values_list("pk", flat=True)
            exclusions_kwargs = {"pk__in": exclusions}
        elif model_field.many_to_one or model_field.one_to_one:
            # Get instance itself as exclusion
            exclusions = instance_field.pk
            exclusions_kwargs = {"pk": exclusions}
        else:
            # Get instance field value as exclusion
            exclusions_kwargs = {field_str: instance_field}

        queryset = queryset.exclude(**exclusions_kwargs)

    results = map(render_page, queryset[:limit])
    return JsonResponse(dict(items=list(results)))


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
