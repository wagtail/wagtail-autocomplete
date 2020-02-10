from django.conf.urls import include, url

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls

from wagtailautocomplete.urls.admin import urlpatterns as autocomplete_admin_urls
from wagtailautocomplete.urls.public import urlpatterns as autocomplete_public_urls


urlpatterns = [
    url(r'^admin/autocomplete/', include(autocomplete_admin_urls)),
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^autocomplete/', include(autocomplete_public_urls)),
    url(r'', include(wagtail_urls)),
]
