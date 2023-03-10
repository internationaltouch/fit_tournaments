# Generated by Django 3.2.16 on 2022-12-27 23:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Country",
            fields=[
                (
                    "iso3166a3",
                    models.CharField(max_length=3, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=100)),
            ],
            options={
                "verbose_name_plural": "countries",
                "ordering": ("name",),
            },
        ),
    ]
