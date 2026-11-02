from django.core.cache import cache
from django.db.models import Count

from .models import Task


def project_stats(project_id):
    key = f"project-stats:{project_id}"
    stats = cache.get(key)
    if stats is None:
        stats = dict(
            Task.objects.filter(project_id=project_id)
            .order_by()
            .values_list("status")
            .annotate(n=Count("id"))
        )
        cache.set(key, stats, timeout=300)  # always set a TTL
    return stats
