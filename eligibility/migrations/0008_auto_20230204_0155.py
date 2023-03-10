# Generated by Django 3.2.16 on 2023-02-04 01:55

from django.db import migrations

import eligibility.fields


class Migration(migrations.Migration):

    dependencies = [
        ("eligibility", "0007_auto_20230121_2347"),
    ]

    operations = [
        migrations.AlterField(
            model_name="grandparent",
            name="adopted",
            field=eligibility.fields.BooleanField(
                default=False,
                help_text="Tick if this parental relationship is not biological.",
            ),
        ),
        migrations.AlterField(
            model_name="parent",
            name="adopted",
            field=eligibility.fields.BooleanField(
                default=False,
                help_text="Tick if this parental relationship is not biological.",
            ),
        ),
    ]
