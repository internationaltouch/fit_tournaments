import uuid

from django.db import models
from django.core.exceptions import ValidationError


class Country(models.Model):
    iso3166a3 = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "countries"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Player(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    country_of_birth = models.ForeignKey(
        Country,
        blank=True,
        null=True,
        help_text="If not one of these countries, leave blank and type below.",
        on_delete=models.PROTECT,
        related_name="players_born",
    )
    country_of_birth_other = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default=None,
        help_text="Only valid if not one of the countries listed above.",
    )
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

    def __str__(self):
        return self.name

    def clean(self):
        country_names = {
            c.lower() for c in Country.objects.values_list("name", flat=True)
        }
        errors = {}

        if self.country_of_birth_other:
            if self.country_of_birth:
                errors.setdefault("country_of_birth_other", []).append(
                    "You may only provide a custom country of birth "
                    "if you have not selected from the above."
                )
            if self.country_of_birth_other.strip().lower() in country_names:
                errors.setdefault("country_of_birth_other", []).append(
                    "You can't manually type in a country of birth "
                    "that appears in the list above."
                )

        if self.residence_other:
            if self.residence:
                errors.setdefault("residence_other", []).append(
                    "You may only provide a custom country of residence "
                    "if you have not selected from the above."
                )
            if self.residence_other.strip().lower() in country_names:
                errors.setdefault("residence_other", []).append(
                    "You can't manually type in a country of residence "
                    "that appears in the list above."
                )

        if errors:
            raise ValidationError(errors)
