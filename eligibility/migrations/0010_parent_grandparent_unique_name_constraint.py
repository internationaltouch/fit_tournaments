# Generated by Django 3.2.16 on 2023-02-11 00:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("eligibility", "0009_auto_20230204_0207"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="parent",
            options={},
        ),
        migrations.AlterUniqueTogether(
            name="grandparent",
            unique_together={("child", "name")},
        ),
        migrations.AlterUniqueTogether(
            name="parent",
            unique_together={("child", "name")},
        ),
    ]