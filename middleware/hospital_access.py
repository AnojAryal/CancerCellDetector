from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import jwt
from jwt.exceptions import InvalidTokenError


class HospitalAccessMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print("Request received:", request.method, request.url)
        current_user = None
        if (
            request.url.path.startswith("/docs")
            or request.url.path.startswith("/redoc")
            or request.url.path == "/openapi.json"
        ):
            print("Skipping middleware for documentation endpoint:", request.url.path)
            response = await call_next(request)
            return response

        try:
            # Extract the token from the request headers
            authorization_header = request.headers.get("Authorization")
            if authorization_header:
                parts = authorization_header.split()

                if len(parts) == 2 and parts[0] == "Bearer":
                    token = parts[1]
                    # Decode the token
                    decoded_token = jwt.decode(
                        token,
                        "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
                        algorithms=["HS256"],
                    )
                    print(f"decoded token: {decoded_token}")
                    current_user = decoded_token

        except InvalidTokenError as e:
            print("Invalid token:", e)
            pass
        except Exception as e:
            print("Error:", e)
            pass

        if current_user and current_user.get("is_admin"):
            print("Admin user detected. Allowing access.")
            response = await call_next(request)
            return response

        if current_user and not current_user.get("hospital_id"):
            print("Non-admin user without hospital affiliation. Access denied.")
            return Response("Forbidden", status_code=403)

        print("Request processing complete.")
        response = await call_next(request)
        return response
