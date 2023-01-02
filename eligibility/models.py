import uuid
from typing import List

from django.db import models

from eligibility.managers import PersonManager, PlayerDeclarationManager, PlayerManager
from eligibility.utils import person_clean, person_declaration_clean


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
        ordering = ("name",)

    def __str__(self):
        return self.name

    def clean(self):
        country_names = {
            c.lower() for c in Country.objects.values_list("name", flat=True)
        }
        person_clean(self, country_names)

    def eligible(self) -> List[str]:
        """
        Query across Parent and GrandParent relations for all eligibilities.
        """
        countries = {self.birthplace, self.residency}
        countries |= set(self.parent_set.values_list("birthplace", flat=True))
        for p in self.parent_set.all():
            countries |= set(p.grandparent_set.values_list("birthplace", flat=True))
        return sorted(countries)


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

    objects = PlayerManager()


class Parent(Person):
    child = models.ForeignKey(Player, on_delete=models.PROTECT)
    adopted = models.BooleanField(
        help_text="Tick if this parental relationship is not biological.",
    )

    objects = PersonManager()


class GrandParent(Person):
    child = models.ForeignKey(Parent, on_delete=models.PROTECT)
    adopted = models.BooleanField(
        help_text="Tick if this parental relationship is not biological.",
    )

    objects = PersonManager()

    class Meta:
        verbose_name = "grandparent"


class PlayerDeclaration(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    player = models.ForeignKey(
        Player, related_name="declarations", on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        help_text="Automatically recorded time that the declaration was saved.",
    )
    name = models.CharField(
        # Despite having a fkey back to the Player, we want to trap the content that
        # was current at the time they made the declaration, so this redundancy is
        # acceptable.
        editable=False,
        max_length=100,
        help_text="Name of the player that made this declaration.",
    )
    eligible_for = models.JSONField(
        # We could extract this from the "data" field (below) however that would
        # require the logic to be baked in too (as this policy changes over time, we
        # don't need to special case evaluation based on timestamp).
        editable=False,
        help_text=(
            "List of countries that submitted data indicates the player is eligible "
            "to represent."
        ),
    )
    elected_country = models.ForeignKey(
        Country,
        related_name="available_for_selection",
        help_text=(
            "Country that this player has elected to play for, from their available "
            "choices."
        ),
        on_delete=models.PROTECT,
    )
    data = models.JSONField(
        editable=False,
        help_text="Serialized data that locks the values in time.",
    )
    supersceded_by = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    objects = PlayerDeclarationManager()

    def __str__(self):
        return f"{self.name} - {self.elected_country}"

    def clean(self):
        person_declaration_clean(self)
