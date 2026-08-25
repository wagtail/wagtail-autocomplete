from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from wagtailautocomplete.edit_handlers import AutocompletePanel
from wagtailautocomplete.tests.testapp.models import Group, House, Person


class PersonViewSet(SnippetViewSet):
    model = Person
    icon = "user"
    menu_label = "People"
    list_display = ["name", "group"]
    panels = [
        FieldPanel("name"),
        AutocompletePanel("group"),
    ]


class HouseViewSet(SnippetViewSet):
    model = House
    icon = "home"
    menu_label = "Houses"
    list_display = ["name", "owner"]
    panels = [
        FieldPanel("name"),
        AutocompletePanel("owner"),
        AutocompletePanel("occupants"),
    ]


class GroupViewSet(SnippetViewSet):
    model = Group
    icon = "group"
    menu_label = "Groups"
    list_display = ["title"]
    panels = [
        FieldPanel("title"),
        InlinePanel("members", label="Member", panels=[FieldPanel("name")]),
    ]


register_snippet(PersonViewSet)
register_snippet(HouseViewSet)
register_snippet(GroupViewSet)
