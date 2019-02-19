from django.db import models
from modelcluster.fields import ParentalManyToManyField

from wagtailautocomplete.edit_handlers import AutocompletePanel

try:
    # Wagtail 2.x
    from wagtail.core.models import Page
except ImportError:
    # Wagtail 1.x
    from wagtail.wagtailcore.models import Page


class TargetPage(Page):
    pass


class SingleAutocompletePage(Page):
    target = models.ForeignKey(
        TargetPage, on_delete=models.PROTECT
    )

    content_panels = Page.content_panels + [
        AutocompletePanel('target', target_model='testapp.TargetPage'),
    ]


class SingleOptionalAutocompletePage(Page):
    target = models.ForeignKey(
        TargetPage, blank=True, null=True, on_delete=models.PROTECT
    )


class MultipleAutocompletePage(Page):
    targets = ParentalManyToManyField(TargetPage)


class MultipleOptionalAutocompletePage(Page):
    targets = ParentalManyToManyField(TargetPage, blank=True)
