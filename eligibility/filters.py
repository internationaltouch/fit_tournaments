from datetime import date

from django.db.models import Q
from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class DecadeBornListFilter(admin.SimpleListFilter):
    title = _("decade born")
    parameter_name = "decade"

    def lookups(self, request, model_admin):
        return (
            (str(decade), f"{decade} to {decade + 9}")
            for decade in range(1920, date.today().year - 5, 10)
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        return queryset.filter(
            date_of_birth__range=(
                date(int(self.value()), 1, 1),
                date(int(self.value()) + 9, 12, 31),
            ),
        )


class EligibilityListFilter(admin.SimpleListFilter):
    title = _("eligible for")
    parameter_name = "eligible"

    def lookups(self, request, model_admin):
        from .models import Country

        return (
            Country.objects.filter(
                Q(players_born__isnull=False)
                | Q(players_resident__isnull=False)
                | Q(parents_born__isnull=False)
                | Q(grandparents_born__isnull=False)
            )
            .distinct()
            .values_list("name", "name")
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        return queryset.eligible_for(self.value())
