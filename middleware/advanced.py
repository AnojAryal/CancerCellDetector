from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from collections import defaultdict
from typing import Dict
import time
import logging

logger = logging.getLogger(__name__)


class AdvancedMiddleWare(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit: int):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.rate_limit_records: Dict[str, float] = defaultdict(float)
        # Paths exempt from rate limiting
        self.exempt_paths = [
            "/openapi.json",
            "/docs",
            "/redoc",
            "/favicon.ico",
            "/static/CancerDetector/css/bootstrap.css",
            "/static/CancerDetector/js/jquery-slim.js",
            "/static/CancerDetector/js/popper.js",
            "/static/CancerDetector/js/bootstrap.js",
        ]

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        path = request.url.path

        # Skip rate limiting for exempt paths
        if path not in self.exempt_paths:
            if current_time - self.rate_limit_records[client_ip] < self.rate_limit:
                return Response(content="Rate Limit Exceed", status_code=429)
            self.rate_limit_records[client_ip] = current_time

        logger.info(f"Request to {path}")

        # Process the request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Add custom headers without modifying the original headers object
        custom_headers = {"X-Process-Time": str(process_time)}
        for header, value in custom_headers.items():
            response.headers.append(header, value)

        # Asynchronous logging for processing time
        logger.info(f"Response for path {path} took {process_time} seconds")

        return response
