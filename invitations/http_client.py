import logging
import requests
from urllib.parse import urlparse

from invitations.circuit_breaker import (
    record_failure,
    open_circuit,
    close_circuit,
    FAILURE_THRESHOLD,
)
from invitations.middleware_circuit import ExternalServiceBlocked

logger = logging.getLogger(__name__)


def call_external_service(
    *,
    url: str,
    method: str = "GET",
    request=None,
    **kwargs,
):
    """
    Wrapper around requests that enforces circuit breaker.
    """
    domain = urlparse(url).netloc

    # Block if circuit open
    from invitations.middleware_circuit import ExternalServiceCircuitBreakerMiddleware

    ExternalServiceCircuitBreakerMiddleware.block_if_open(domain, request)

    try:
        response = requests.request(method, url, timeout=5, **kwargs)

        if response.status_code >= 500:
            failures = record_failure(domain)

            logger.error(
                "External service failure",
                extra={
                    "trace_id": getattr(request, "trace_id", None),
                    "user_id": (
                        request.user.id
                        if request and request.user.is_authenticated
                        else None
                    ),
                    "tenant_id": getattr(request, "tenant_id", None),
                },
            )

            if failures > FAILURE_THRESHOLD:
                open_circuit(domain)
                logger.error(
                    "Circuit opened",
                    extra={
                        "trace_id": getattr(request, "trace_id", None),
                        "tenant_id": getattr(request, "tenant_id", None),
                    },
                )

        else:
            close_circuit(domain)

        return response

    except ExternalServiceBlocked:
        raise

    except Exception:
        failures = record_failure(domain)
        if failures > FAILURE_THRESHOLD:
            open_circuit(domain)
        raise
