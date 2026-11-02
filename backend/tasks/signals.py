import logging

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Task

logger = logging.getLogger(__name__)


@receiver([post_save, post_delete], sender=Task)
def clear_stats(sender, instance, **kwargs):
    try:
        cache.delete(f"project-stats:{instance.project_id}")
    except Exception:
        logger.warning("could not invalidate stats for project %s", instance.project_id, exc_info=True)