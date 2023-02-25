import uuid
from typing import List

from dirtyfields import DirtyFieldsMixin
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property

from eligibility.fields import BooleanField, JSONField
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


class Person(DirtyFieldsMixin, models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField(help_text="Please use YYYY-MM-DD format.")
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

    def get_absolute_url(self):
        return reverse("player", kwargs={"pk": self.pk})

    def can_declare(self):
        if self.parent_set.exclude(adopted=True).count() < 2:
            raise ValueError("Must have at least two biological parents.")
        for parent in self.parent_set.all():
            if parent.grandparent_set.exclude(adopted=True).count() < 2:
                raise ValueError(
                    "At least one parent does not have at least two biological parents."
                )

    @cached_property
    def can_declare_bool(self):
        try:
            self.can_declare()
        except ValueError:
            return False
        return True

    def unable_to_declare_reason(self):
        try:
            self.can_declare()
        except ValueError as exc:
            return str(exc)


class Parent(Person):
    child = models.ForeignKey(Player, on_delete=models.PROTECT)
    adopted = BooleanField(
        default=False,
        help_text="Tick if this parental relationship is not biological.",
    )

    objects = PersonManager()

    class Meta:
        unique_together = ("child", "name")


class GrandParent(Person):
    child = models.ForeignKey(Parent, on_delete=models.PROTECT)
    adopted = BooleanField(
        default=False,
        help_text="Tick if this parental relationship is not biological.",
    )

    objects = PersonManager()

    class Meta:
        verbose_name = "grandparent"
        unique_together = ("child", "name")


class PlayerDeclaration(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    player = models.ForeignKey(
        Player, related_name="declarations", on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        get_user_model(),
        editable=False,
        related_name="declarations",
        on_delete=models.PROTECT,
        help_text="The user who made this declaration for the player.",
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
    data = JSONField(
        editable=False,
        help_text="Serialized data that locks the values in time.",
    )
    evidence_nation = JSONField(
        null=True,
        editable=False,
        help_text="Record of documents sighted by FIT member.",
    )
    supersceded_by = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    objects = PlayerDeclarationManager()

    class Meta:
        ordering = ("-timestamp",)

    def __str__(self):
        return f"{self.name} - {self.elected_country}"

    def newly_added_ancestors(self):
        """
        The following ancestors were not recorded when the declaration was made; this
        can change the eligibility standing of the individual _if_ an ancestor was born
        in a country not already seen amongst the other ancestors.
        """
        pks = [s.pk for s in self.data]
        ancestors = [
            parent
            for parent in Parent.objects.filter(child=self.player).exclude(pk__in=pks)
        ]
        ancestors += [
            grandparent
            for grandparent in GrandParent.objects.filter(
                child__child=self.player
            ).exclude(pk__in=pks)
        ]
        return ancestors

    def now_eligible_for(self):
        """
        The ForeignKey to Player does not exercise the custom manager, so we need to perform another query.
        """
        return Player.objects.get(pk=self.player.pk).eligible()

    def clean(self):
        person_declaration_clean(self)


class Event(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=256)
    closing_date = models.DateField(
        blank=True, null=True, help_text="Closing date for nominations."
    )
    team_date = models.DateField(
        blank=True, null=True, help_text="Two weeks prior to closing date."
    )
    squad_date = models.DateField(
        blank=True, null=True, help_text="Three months prior to closing date."
    )

    class Meta:
        ordering = ("closing_date",)

    def __str__(self):
        return self.name


class NationalSquad(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    event = models.ForeignKey(Event, related_name="squads", on_delete=models.PROTECT)
    name = models.CharField(max_length=256)
    players = models.ManyToManyField(
        PlayerDeclaration,
        blank=True,
        limit_choices_to=models.Q(supersceded_by__isnull=True),
    )

    class Meta:
        unique_together = ("event", "name")
        ordering = ("event", "name")

    def __str__(self):
        return f"{self.name} - {self.event.name}"


class NationalTeam(models.Model):
    squad = models.OneToOneField(
        NationalSquad, primary_key=True, on_delete=models.PROTECT, editable=False
    )
    players = models.ManyToManyField(PlayerDeclaration, blank=True)

    class Meta:
        unique_together = ("squad",)
        ordering = ("squad",)

    def __str__(self):
        return f"{self.squad.name} - {self.squad.event.name}"
