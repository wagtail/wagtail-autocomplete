from django.templatetags.static import static
from django.utils.html import format_html

from wagtail.core import hooks


@hooks.register('insert_editor_js')
def editor_js():
    html = '<script type="text/javascript" src="{}"></script>'.format(
        static('wagtailautocomplete/dist.js')
    )
    return format_html(html)


@hooks.register('insert_editor_css')
def editor_css():
    html = '<link rel="stylesheet" type="text/css" href="{}" />'.format(
        static('wagtailautocomplete/dist.css')
    )
    return format_html(html)
