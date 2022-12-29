import uuid

from django.db import models
from eligibility.utils import person_clean


class Country(models.Model):
    iso3166a3 = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "countries"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Person(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    country_of_birth = models.ForeignKey(
        Country,
        blank=True,
        null=True,
        help_text="If not one of these countries, leave blank and type below.",
        on_delete=models.PROTECT,
        related_name="%(class)ss_born",
    )
    country_of_birth_other = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default=None,
        help_text="Only valid if not one of the countries listed above.",
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def clean(self):
        country_names = {
            c.lower() for c in Country.objects.values_list("name", flat=True)
        }
        person_clean(self, country_names)


class Player(Person):
    residence = models.ForeignKey(
        Country,
        blank=True,
        null=True,
        help_text="If not one of these countries, leave blank and type below.",
        on_delete=models.PROTECT,
        related_name="players_resident",
    )
    residence_other = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default=None,
        help_text="Only valid if not one of the countries listed above.",
    )


class Parent(Person):
    child = models.ForeignKey(Player, on_delete=models.PROTECT)


class GrandParent(Person):
    child = models.ForeignKey(Parent, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "grandparent"
