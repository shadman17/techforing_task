from datetime import timedelta
import time
from django.core.cache import cache

FAILURE_THRESHOLD = 3
FAILURE_WINDOW_SECONDS = 60
CIRCUIT_OPEN_SECONDS = 120

CIRCUIT_PREFIX = "circuit"
FAILURE_PREFIX = "failures"


def _failure_key(domain):
    return f"{FAILURE_PREFIX}:{domain}"


def _circuit_key(domain):
    return f"{CIRCUIT_PREFIX}:{domain}"


def is_circuit_open(domain: str) -> bool:
    return cache.get(_circuit_key(domain)) is True


def record_failure(domain: str) -> int:
    """
    Record a failure and return current failure count
    """
    key = _failure_key(domain)
    failures = cache.get(key, [])

    now = time.time()
    failures.append(now)

    failures = [ts for ts in failures if now - ts <= FAILURE_WINDOW_SECONDS]

    cache.set(key, failures, timeout=FAILURE_WINDOW_SECONDS)
    return len(failures)


def open_circuit(domain: str):
    cache.set(_circuit_key(domain), True, timeout=CIRCUIT_OPEN_SECONDS)


def close_circuit(domain: str):
    cache.delete(_circuit_key(domain))
    cache.delete(_failure_key(domain))
