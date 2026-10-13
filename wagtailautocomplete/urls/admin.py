from django.urls import re_path
from wagtail.admin.auth import require_admin_access

from wagtailautocomplete.views import create, objects, search

urlpatterns = [
    re_path(r"^create/", require_admin_access(create)),
    # Explicitly override public allowlist checks for admin endpoints
    re_path(r"^objects/", require_admin_access(objects), {"public": False}),
    re_path(r"^search/", require_admin_access(search), {"public": False}),
]
