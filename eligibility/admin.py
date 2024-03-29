import nested_admin
from django.contrib import admin
from guardian.admin import GuardedModelAdmin, GuardedModelAdminMixin
from more_admin_filters import RelatedDropdownFilter

from eligibility.filters import (
    DecadeBornListFilter,
    ElectedCountryListFilter,
    EligibilityListFilter,
    IsSuperscededListFilter,
)
from eligibility.forms import PlayerDeclarationAdminForm
from eligibility.models import (
    Country,
    DeclarationExceptionRequest,
    Event,
    GrandParent,
    NationalSquad,
    NationalTeam,
    Parent,
    Player,
    PlayerDeclaration,
)


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
    list_per_page = 25


@admin.register(Parent)
class ParentAdmin(nested_admin.NestedModelAdmin):
    list_display = ("name", "country_of_birth", "child")
    list_per_page = 25
    inlines = [
        GrandParentInline,
    ]


@admin.register(Player)
class PlayerAdmin(GuardedModelAdminMixin, nested_admin.NestedModelAdmin):
    list_display = ("name", "date_of_birth", "country_of_birth", "eligible")
    list_per_page = 10
    list_filter = (EligibilityListFilter, DecadeBornListFilter)
    inlines = [
        ParentInline,
        PlayerDeclarationInline,
    ]


@admin.register(DeclarationExceptionRequest)
class DeclarationExceptionRequestAdmin(GuardedModelAdmin):
    list_display = ("pk", "player")
    list_per_page = 25


@admin.register(PlayerDeclaration)
class PlayerDeclarationAdmin(GuardedModelAdmin):
    form_class = PlayerDeclarationAdminForm
    list_display = ("name", "author", "elected_country", "timestamp", "supersceded_by")
    list_per_page = 25
    list_filter = (
        ElectedCountryListFilter,
        IsSuperscededListFilter.init("is_supersceded"),
        ("player", RelatedDropdownFilter),
        ("author", RelatedDropdownFilter),
        ("verified_by", RelatedDropdownFilter),
    )
    readonly_fields = (
        "name",
        "author",
        "eligible_for",
        "supersceded_by",
        "data",
        "evidence_nation",
    )


@admin.register(Event)
class EventAdmin(GuardedModelAdmin):
    list_display = ("name", "closing_date", "team_date", "squad_date")
    list_filter = ("closing_date", "team_date", "squad_date")
    list_editable = ("closing_date", "team_date", "squad_date")


@admin.register(NationalSquad)
class NationalSquadAdmin(GuardedModelAdmin):
    list_display = ("name", "event")
    list_filter = ("event",)


admin.site.register(NationalTeam, GuardedModelAdmin)
