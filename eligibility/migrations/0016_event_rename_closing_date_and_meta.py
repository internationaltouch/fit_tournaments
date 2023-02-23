# Generated by Django 3.2.17 on 2023-02-13 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("eligibility", "0015_event_nationalsquad"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="event",
            options={"ordering": ("closing_date",)},
        ),
        migrations.RenameField(
            model_name="event",
            old_name="start_date",
            new_name="closing_date",
        ),
        migrations.AlterField(
            model_name="event",
            name="closing_date",
            field=models.DateField(
                blank=True, help_text="Closing date for nominations.", null=True
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="squad_date",
            field=models.DateField(
                blank=True, help_text="Three months prior to closing date.", null=True
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="team_date",
            field=models.DateField(
                blank=True, help_text="Two weeks prior to closing date.", null=True
            ),
        ),
        migrations.AlterField(
            model_name="nationalsquad",
            name="players",
            field=models.ManyToManyField(
                blank=True,
                limit_choices_to=models.Q(("supersceded_by__isnull", True)),
                to="eligibility.PlayerDeclaration",
            ),
        ),
    ]
