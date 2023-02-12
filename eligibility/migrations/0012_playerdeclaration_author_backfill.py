# Generated by Django 3.2.17 on 2023-02-11 12:31

from django.db import migrations
from guardian.shortcuts import get_users_with_perms


def find_author_from_guardian_permissions(apps, schema_editor):
    PlayerDeclaration = apps.get_model("eligibility", "PlayerDeclaration")
    for declaration in PlayerDeclaration.objects.defer("data"):
        qs = get_users_with_perms(declaration.player, with_group_users=False)
        if qs.exists():
            declaration.author_id = qs.first().pk
            declaration.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("eligibility", "0011_playerdeclaration_author"),
    ]

    operations = [migrations.RunPython(find_author_from_guardian_permissions, noop)]
