import uuid
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class TraceIDMiddleware(MiddlewareMixin):
    """
    - Reads X-Trace-ID header if present
    - Otherwise generates a new trace_id
    - Attaches it to request and logging context
    """

    def process_request(self, request):
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        request.trace_id = trace_id

    def process_response(self, request, response):
        trace_id = getattr(request, "trace_id", None)
        if trace_id:
            response["X-Trace-ID"] = trace_id
        return response
