import nested_admin
from django.contrib import admin
from more_admin_filters import RelatedDropdownFilter

from eligibility.filters import (
    DecadeBornListFilter,
    ElectedCountryListFilter,
    EligibilityListFilter,
    IsSuperscededListFilter,
)
from eligibility.models import Country, GrandParent, Parent, Player, PlayerDeclaration


class GrandParentInline(nested_admin.NestedTabularInline):
    model = GrandParent
    extra = 0


class ParentInline(nested_admin.NestedTabularInline):
    model = Parent
    extra = 0
    inlines = [
        GrandParentInline,
    ]


class PlayerDeclarationInline(nested_admin.NestedTabularInline):
    model = PlayerDeclaration
    extra = 0


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "iso3166a3")


@admin.register(GrandParent)
class GrandParentAdmin(nested_admin.NestedModelAdmin):
    list_display = ("name", "country_of_birth", "child")


@admin.register(Parent)
class ParentAdmin(nested_admin.NestedModelAdmin):
    list_display = ("name", "country_of_birth", "child")
    inlines = [
        GrandParentInline,
    ]


@admin.register(Player)
class PlayerAdmin(nested_admin.NestedModelAdmin):
    list_display = ("name", "date_of_birth", "country_of_birth", "eligible")
    list_filter = (EligibilityListFilter, DecadeBornListFilter)
    inlines = [
        ParentInline,
        PlayerDeclarationInline,
    ]


@admin.register(PlayerDeclaration)
class PlayerDeclarationAdmin(admin.ModelAdmin):
    list_display = ("name", "elected_country", "timestamp", "supersceded_by")
    list_filter = (
        ElectedCountryListFilter,
        IsSuperscededListFilter.init("is_supersceded"),
        ("player", RelatedDropdownFilter),
    )
    fields = (
        "player",
        "name",
        "eligible_for",
        "elected_country",
        "supersceded_by",
        "data",
    )
    readonly_fields = ("name", "eligible_for", "supersceded_by", "data")
