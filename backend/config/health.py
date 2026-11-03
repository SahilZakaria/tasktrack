import logging

from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def health(request):
    checks = {}

    try:
        with connection.cursor() as c:
            c.execute("SELECT 1")
        checks["db"] = "ok"
    except Exception:
        logger.warning("health check: database unavailable", exc_info=True)
        checks["db"] = "down"

    try:
        cache.set("health-check", "1", timeout=5)
        checks["cache"] = "ok" if cache.get("health-check") == "1" else "down"
    except Exception:
        logger.warning("health check: cache unavailable", exc_info=True)
        checks["cache"] = "down"

    healthy = checks["db"] == "ok"
    overall = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    return JsonResponse({"status": overall, **checks}, status=200 if healthy else 503)