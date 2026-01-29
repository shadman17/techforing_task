import logging
from django.conf import settings


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        record.service = getattr(settings, "SERVICE_NAME", "unknown")

        record.trace_id = getattr(record, "trace_id", None)
        record.user_id = getattr(record, "user_id", None)
        record.tenant_id = getattr(record, "tenant_id", None)

        return True
