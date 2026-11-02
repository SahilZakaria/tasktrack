from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse


def health(request):
    checks = {}

    try:
        with connection.cursor() as c:
            c.execute("SELECT 1")
        checks["db"] = "ok"
    except Exception:
        checks["db"] = "down"

    try:
        cache.set("health-check", "1", timeout=5)
        checks["cache"] = "ok" if cache.get("health-check") == "1" else "down"
    except Exception:
        checks["cache"] = "down"

    healthy = checks["db"] == "ok"
    overall = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    return JsonResponse({"status": overall, **checks}, status=200 if healthy else 503)