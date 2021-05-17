from django.db import models

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel


class House(ClusterableModel):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey('Person', models.PROTECT, help_text="the owner")
    occupants = ParentalManyToManyField('Person', related_name='houses')


class Group(ClusterableModel):
    title = models.CharField(max_length=50)

    @classmethod
    def autocomplete_create(kls: type, value: str):
        return kls.objects.create(title=value)


class Person(models.Model):
    name = models.CharField(max_length=50)
    group = ParentalKey(Group, on_delete=models.SET_NULL, related_name='members', null=True)

    autocomplete_search_field = 'name'

    def autocomplete_label(self):
        return self.name
