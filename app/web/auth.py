import os

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Route
from starlette.templating import Jinja2Templates

from app.web.security import generate_csrf_token

templates = Jinja2Templates(directory="app/templates")
ph = PasswordHasher()


def get_admin_credentials():
    return os.getenv("ADMIN_USERNAME", "admin"), os.getenv("ADMIN_PASSWORD_HASH", "")


async def login_get(request: Request):
    if request.session.get("admin_logged_in"):
        return RedirectResponse(url="/admin", status_code=303)

    return templates.TemplateResponse(
        request, "admin/login.html", {"csrf_token": generate_csrf_token(request)}
    )


async def login_post(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    expected_username, expected_hash = get_admin_credentials()

    error = None
    if not expected_hash:
        error = "Admin password hash not configured on server."
    elif username != expected_username:
        error = "Invalid credentials."
    else:
        try:
            ph.verify(expected_hash, str(password))
            # Login success
            request.session["admin_logged_in"] = True
            return RedirectResponse(url="/admin", status_code=303)
        except VerifyMismatchError:
            error = "Invalid credentials."

    return templates.TemplateResponse(
        request,
        "admin/login.html",
        {"error": error, "csrf_token": generate_csrf_token(request)},
        status_code=401,
    )


async def logout_post(request: Request):
    request.session.pop("admin_logged_in", None)
    return RedirectResponse(url="/admin/login", status_code=303)


def requires_auth(endpoint):
    """Decorator to protect admin routes."""

    async def wrapper(request: Request, *args, **kwargs):
        if not request.session.get("admin_logged_in"):
            return RedirectResponse(url="/admin/login", status_code=303)
        return await endpoint(request, *args, **kwargs)

    return wrapper


routes = [
    Route("/admin/login", endpoint=login_get, methods=["GET"]),
    Route("/admin/login", endpoint=login_post, methods=["POST"]),
    Route("/admin/logout", endpoint=logout_post, methods=["POST"]),
]
