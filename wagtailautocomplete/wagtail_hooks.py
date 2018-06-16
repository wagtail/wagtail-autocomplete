from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.html import format_html

try:
    # Wagtail 2.x
    from wagtail.core import hooks
except ImportError:
    # Wagtail 1.x
    from wagtail.wagtailcore import hooks


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
