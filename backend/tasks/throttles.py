import logging

from rest_framework.throttling import UserRateThrottle

logger = logging.getLogger(__name__)


class FailOpenUserRateThrottle(UserRateThrottle):
    def allow_request(self, request, view):
        try:
            return super().allow_request(request, view)
        except Exception:
            logger.warning("throttle cache unavailable, allowing request", exc_info=True)
            return True