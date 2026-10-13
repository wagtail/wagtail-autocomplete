from functools import partial
from http import HTTPStatus
from urllib.parse import unquote

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db.models import Model, QuerySet
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotFound,
    JsonResponse,
)
from django.utils.module_loading import import_string
from django.views.decorators.http import require_GET, require_POST
from wagtail.models import Page

from wagtailautocomplete.allowed import AllowRule, live_pages

# Default models and allowed checks for the public endpoints' allowlist
WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS_DEFAULT: dict[str, list[AllowRule | str]] = {
    "wagtailcore.Page": [
        "wagtailautocomplete.allowed.live_pages",
        "wagtailautocomplete.allowed.viewable_pages",
    ],
    "wagtaildocs.Document": ["wagtailautocomplete.allowed.viewable_documents"],
}


def render_page(page):
    if getattr(page, "specific", None):
        # For support of non-Page models like Snippets.
        page = page.specific
    if callable(getattr(page, "autocomplete_label", None)):
        title = page.autocomplete_label()
    else:
        title = page.title
    return {"pk": page.pk, "title": title}


def get_public_models() -> dict[type[Model], list[AllowRule | str]]:
    """
    Return the public allowlist as a dict of model classes to allow rules.
    Raises ImproperlyConfigured if a label in the setting doesn't resolve to
    an installed model.
    """
    allowlist = getattr(
        settings,
        "WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS",
        WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS_DEFAULT,
    )

    public_models = {}
    for label, rules in allowlist.items():
        try:
            public_models[apps.get_model(label)] = rules
        except (LookupError, ValueError) as err:
            # If wagtail.documents isn't in INSTALLED_APPS, our default for
            # "wagtaildocs.Document" will raise here. Let it pass.
            if allowlist is WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS_DEFAULT:
                continue
            raise ImproperlyConfigured(
                f"WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS: {label!r} is not "
                "an installed model"
            ) from err

    return public_models


def exclude_model(
    queryset: QuerySet, request: HttpRequest, model: type[Model]
) -> QuerySet:
    """Exclude instances of the given model from the queryset."""
    return queryset.exclude(pk__in=model._base_manager.values("pk"))


def get_public_rules(model: type[Model]) -> list[AllowRule | str] | None:
    """
    Return the public allow rules for a model from the allowlist.

    This can come from either the model itself or a parent class that's in
    the allowlist. Returns None if the model is not in the allowlist or if
    its allowed checks are empty. Subclasses of the model that are denied
    in the allowlist are excluded before the model's rules are applied.
    """
    public_models = get_public_models()

    # Get the first of rules that apply to this model, or its ancestors
    rules = next(
        (
            public_models[cls]
            for cls in [model, *model._meta.get_parent_list()]
            if cls in public_models
        ),
        None,
    )
    if not rules:
        return None

    # If there's a subclass of the given model that is also in the public
    # models, and that subclass has an empty set of rules, we need to
    # exclude it. Add a checker function that will deny instances of that
    # subclass.
    rules = [
        partial(exclude_model, model=cls)
        for cls, cls_rules in public_models.items()
        if not cls_rules and issubclass(cls, model)
    ] + rules

    return rules


def get_model(model_label: str, public: bool) -> type[Model] | None:
    """
    Resolve a model label to a model class. Returns None if the model does not
    exist or, for public requests, is not in the public allowlist.
    """
    try:
        model = apps.get_model(model_label)
    except (LookupError, ValueError):
        return None

    if public and get_public_rules(model) is None:
        return None

    return model


def apply_allow_rules(
    queryset: QuerySet, model: type[Model], request: HttpRequest, public: bool
) -> QuerySet:
    """
    Apply the allow rules for public requests, or exclude draft pages
    for admin requests.
    """
    rules: list[AllowRule | str] | None = []

    if public:
        rules = get_public_rules(model)
    elif issubclass(model, Page):
        # Always filter pages for live-ness, whether public or not, so
        # that only "live" pages are selectable in the AutocompletePanel
        rules = [live_pages]

    for rule in rules:
        if isinstance(rule, str):
            rule = import_string(rule)
        queryset = rule(queryset, request)

    return queryset


@require_GET
def objects(request: HttpRequest, public: bool = True) -> HttpResponse:
    """
    Return objects of the model given by the `type` GET parameter (default
    `wagtailcore.Page`) whose primary keys are listed in the comma-separated
    `pks` parameter. 404s if any of them is missing or not allowed.

    This view can be used for public autocomplete, when public=True, in which
    case the model must be in WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS and its
    allow rules are applied. It can also be used for private, admin-based
    autocomplete, when public=False, which skips the allow-list checks, so any
    model can be requested, and only draft Wagtail pages are excluded.
    """
    pks_param = request.GET.get("pks")
    if not pks_param:
        return HttpResponseBadRequest()

    model = get_model(request.GET.get("type", "wagtailcore.Page"), public)
    if model is None:
        return HttpResponseBadRequest()

    try:
        pks = [unquote(pk) for pk in pks_param.split(",")]
        queryset = model.objects.filter(pk__in=pks)
    except (TypeError, ValueError, ValidationError):
        return HttpResponseBadRequest()

    queryset = apply_allow_rules(queryset, model, request, public)

    if queryset.count() != len(pks):
        return HttpResponseNotFound("Some objects are either missing or deleted")

    results = map(render_page, queryset)
    return JsonResponse({"items": list(results)})


@require_POST
def search(request: HttpRequest, public: bool = True) -> HttpResponse:
    """
    Search the model given by the `type` POST parameter (default
    `wagtailcore.Page`) for the `query` parameter, returning at most `limit`
    results and leaving out the comma-separated primary keys in `exclude`.

    This view can be used for public autocomplete, when public=True, in which
    case the model must be in WAGTAILAUTOCOMPLETE_ALLOW_PUBLIC_MODELS and its
    allow rules are applied. It can also be used for private, admin-based
    autocomplete, when public=False, which skips the allow-list checks, so any
    model can be requested, and only draft Wagtail pages are excluded.
    """
    search_query = request.POST.get("query", "")
    model = get_model(request.POST.get("type", "wagtailcore.Page"), public)
    if model is None:
        return HttpResponseBadRequest()

    try:
        limit = int(request.POST.get("limit", 100))
    except ValueError:
        return HttpResponseBadRequest()

    if callable(getattr(model, "autocomplete_custom_queryset_filter", None)):
        queryset = model.autocomplete_custom_queryset_filter(
            search_query, request=request
        )
        validate_queryset(queryset, model)
    else:
        queryset = filter_queryset(search_query, model)

    queryset = apply_allow_rules(queryset, model, request, public)

    exclude = request.POST.get("exclude", "")
    if exclude:
        exclusions = [unquote(item) for item in exclude.split(",") if item]
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
