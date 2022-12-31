import nested_admin
from django.contrib import admin

from eligibility.filters import DecadeBornListFilter, EligibilityListFilter
from eligibility.models import Country, GrandParent, Parent, Player


class GrandParentInline(nested_admin.NestedTabularInline):
    model = GrandParent
    extra = 0


class ParentInline(nested_admin.NestedTabularInline):
    model = Parent
    extra = 0
    inlines = [
        GrandParentInline,
    ]


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
    ]
