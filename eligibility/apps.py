from django.apps import AppConfig
from django.db.models.signals import post_save

from eligibility.signals import player_declaration_post_save


class EligibilityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "eligibility"

    def ready(self):
        from .models import PlayerDeclaration

        post_save.connect(player_declaration_post_save, sender=PlayerDeclaration)
