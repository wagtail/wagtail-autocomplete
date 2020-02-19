import wagtail
from django.conf.urls import url
from wagtailautocomplete.views import create, objects, search

if wagtail.VERSION >= (2, 8):
    from wagtail.admin.auth import require_admin_access
else:
    from wagtail.admin.decorators import require_admin_access

urlpatterns = [
    url(r'^create/', require_admin_access(create)),
    url(r'^objects/', require_admin_access(objects)),
    url(r'^search/', require_admin_access(search)),
]
