from django.contrib import admin

from eligibility.models import Country, Player


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "iso3166a3")


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name", "date_of_birth", "country_of_birth")
