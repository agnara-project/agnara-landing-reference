from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # In a real production app, configure CSP carefully.
        # response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


def verify_csrf_token(request: Request, form_token: str) -> bool:
    session_token = request.session.get("csrf_token")
    if not session_token or not form_token:
        return False
    # Use constant time comparison if possible, simple equality for reference
    import hmac

    return hmac.compare_digest(session_token, form_token)


def generate_csrf_token(request: Request) -> str:
    import secrets

    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_hex(32)
    return request.session["csrf_token"]
