# Generated by Django 3.2.17 on 2023-07-20 13:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eligibility", "0020_playerdeclaration_verified"),
    ]

    operations = [
        migrations.AlterField(
            model_name="playerdeclaration",
            name="verified_comments",
            field=models.TextField(
                blank=True,
                help_text="Brief details of what was sighted during the verification process.",
                null=True,
            ),
        ),
    ]
