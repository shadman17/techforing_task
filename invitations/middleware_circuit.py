import logging
from urllib.parse import urlparse

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from invitations.circuit_breaker import is_circuit_open

logger = logging.getLogger(__name__)


class ExternalServiceCircuitBreakerMiddleware(MiddlewareMixin):
    """
    Blocks outbound calls when circuit is OPEN.
    """

    def process_request(self, request):
        # nothing here (outbound calls happen later)
        pass

    @staticmethod
    def block_if_open(domain: str, request):
        if is_circuit_open(domain):
            logger.warning(
                "Circuit open – outbound request blocked",
                extra={
                    "trace_id": getattr(request, "trace_id", None),
                    "user_id": (
                        request.user.id if request.user.is_authenticated else None
                    ),
                    "tenant_id": getattr(request, "tenant_id", None),
                },
            )
            raise ExternalServiceBlocked(f"Circuit open for {domain}")


class ExternalServiceBlocked(Exception):
    pass
