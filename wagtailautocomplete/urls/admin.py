from django.urls import re_path
try:
    from wagtail.admin.decorators import require_admin_access
except ImportError:
    from wagtail.admin.auth import require_admin_access

from wagtailautocomplete.views import create, objects, search

urlpatterns = [
    re_path(r'^create/', require_admin_access(create)),
    re_path(r'^objects/', require_admin_access(objects)),
    re_path(r'^search/', require_admin_access(search)),
]
