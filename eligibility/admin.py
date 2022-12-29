from django.contrib import admin

from eligibility.models import Country, GrandParent, Parent, Player


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "iso3166a3")


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name", "date_of_birth", "country_of_birth")


class ParentAdmin(admin.ModelAdmin):
    list_display = ("name", "country_of_birth", "child")


admin.site.register(Parent, ParentAdmin)
admin.site.register(GrandParent, ParentAdmin)
