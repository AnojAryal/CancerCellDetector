from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.datastructures import Headers
import time
import logging

# Initialize logger
logger = logging.getLogger(__name__)


# middleware class
class AdvancedMiddleWare(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

        # exempt paths
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
        # Extract path from request URL
        path = request.url.path

        # Skip processing for exempt paths
        if path not in self.exempt_paths:
            # Log details of incoming request
            logger.info(f"Incoming request: {request.method} {path}")
            logger.debug(f"Request headers: {request.headers}")

            # Log request body for POST, PUT, PATCH requests
            if request.method in ["POST", "PUT", "PATCH"]:
                logger.debug(f"Request body: {await request.body()}")

        try:
            # Measure start time
            start_time = time.time()

            # Call the next middleware in the chain or handler
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Add custom headers to response
            custom_headers = {"X-Process-Time": str(process_time)}
            for header, value in custom_headers.items():
                response.headers.append(header, value)

            # Log details of response
            logger.info(
                f"Response: {response.status_code} for {request.method} {path} took {process_time:.6f} seconds"
            )

            return response
        except Exception as e:
            # Log and handle exceptions
            logger.exception(f"Error processing request: {e}")

            # Return internal server error response
            return Response(
                content="Internal Server Error",
                status_code=500,
                headers=Headers({"Content-Type": "text/plain"}),
            )
