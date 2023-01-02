def player_declaration_post_save(sender, instance, created, **kwargs):
    if created:
        past = instance.player.declarations.exclude(pk=instance.pk)
        last = past.latest("timestamp")
        if last.supersceded_by is not None:
            raise ValueError(
                f"The last submitted declaration by {instance.player} was already "
                f"marked as supersceded."
            )
        if past.filter(supersceded_by__isnull=True).count() > 1:
            raise ValueError(
                f"There should only be one declaration by {instance.player} that is "
                f"not supersceded."
            )
        past.filter(pk=last.pk).update(supersceded_by=instance)
