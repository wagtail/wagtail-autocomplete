from django.conf.urls import url
try:
    from wagtail.admin.decorators import require_admin_access
except ImportError:
    from wagtail.admin.auth import require_admin_access

from wagtailautocomplete.views import create, objects, search

urlpatterns = [
    url(r'^create/', require_admin_access(create)),
    url(r'^objects/', require_admin_access(objects)),
    url(r'^search/', require_admin_access(search)),
]
