import logging
from functools import wraps

LOG = logging.getLogger(__name__)


def disable_for_loaddata(signal_handler):
    """
    Decorator that turns off signal handlers when loading
    fixture data.
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        raw = kwargs.get("raw", False)
        if raw:
            instance = kwargs.get("instance")
            LOG.debug(
                "Skipping signal handler %r for instance %r.", signal_handler, instance
            )
            return
        signal_handler(*args, **kwargs)

    return wrapper


@disable_for_loaddata
def player_declaration_post_save(sender, instance, created, **kwargs):
    if created:
        past = instance.player.declarations.exclude(pk=instance.pk)
        if not past.exists():
            return
        last = past.latest("timestamp")
        if last.supersceded_by is not None:
            raise ValueError(
                f"The last submitted declaration by {instance.player} ({last.pk}) was "
                f"already marked as supersceded."
            )
        if past.filter(supersceded_by__isnull=True).count() > 1:
            raise ValueError(
                f"There should only be one declaration by {instance.player} that is "
                f"not supersceded."
            )
        past.filter(pk=last.pk).update(supersceded_by=instance)
