# Generated by Django 3.2.17 on 2023-02-12 02:29

from django.db import migrations

import eligibility.fields


class Migration(migrations.Migration):

    dependencies = [
        ("eligibility", "0013_alter_playerdeclaration_author"),
    ]

    operations = [
        migrations.AddField(
            model_name="playerdeclaration",
            name="evidence_nation",
            field=eligibility.fields.JSONField(
                editable=False,
                help_text="Record of documents sighted by FIT member.",
                null=True,
            ),
        ),
    ]
