import os
from contextlib import asynccontextmanager

from agnara import Agnara
from agnara.di import DIRegistry, provider
from agnara_http import Binding, BindingSource, Http
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.staticfiles import StaticFiles

import app.capabilities.admin  # ensure they are registered
import app.capabilities.contacts  # ensure they are registered

# Import Agnara instances
from app.capabilities import app as agnara_core
from app.capabilities.contacts import submit_contact
from app.domain.repositories import ContactRepository

# Implemented by us
from app.infrastructure.database import AsyncSessionLocal, init_db
from app.infrastructure.repositories import SqlAlchemyContactRepository
from app.web.admin_routes import routes as admin_routes
from app.web.auth import routes as auth_routes
from app.web.public_routes import routes as public_routes
from app.web.security import SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(app: Starlette):
    # Initialize Database
    await init_db()

    # Setup Dependency Injection in Agnara
    # We do this when compiling the HttpApplication below.

    yield
    # Cleanup logic (if any)


# Configure Middlewares
session_secret = os.getenv("SESSION_SECRET", "fallback-dev-secret-key-change-me")
secure_cookies = os.getenv("SECURE_COOKIES", "false").lower() == "true"

middleware = [
    Middleware(
        SessionMiddleware,
        secret_key=session_secret,
        https_only=secure_cookies,
        same_site="lax",
    ),
    Middleware(SecurityHeadersMiddleware),
]


# Health check route
async def health_check(request):
    return JSONResponse({"status": "ok"})


routes = [
    Route("/health", endpoint=health_check, methods=["GET"]),
]
routes.extend(public_routes)
routes.extend(auth_routes)
routes.extend(admin_routes)

# Create the Starlette App (Host)
starlette_app = Starlette(
    debug=os.getenv("APP_ENV") == "development",
    routes=routes,
    middleware=middleware,
    lifespan=lifespan,
)

# Mount Static Files
if os.path.exists("app/static"):
    starlette_app.mount("/static", StaticFiles(directory="app/static"), name="static")

project = Agnara("landing")
project.include(agnara_core)
compiled_core = project.compile()


@provider()
def provide_repo() -> ContactRepository:
    return SqlAlchemyContactRepository(AsyncSessionLocal)


di = DIRegistry()
di.bind(ContactRepository, provide_repo)

agnara_http = (
    Http("api")
    .post(
        "/api/contact",
        submit_contact,
        Binding("name", BindingSource.FORM),
        Binding("email", BindingSource.FORM),
        Binding("message", BindingSource.FORM),
        Binding("company", BindingSource.FORM),
        Binding("phone", BindingSource.FORM),
        Binding("subject", BindingSource.FORM),
    )
    .compile(compiled_core, dependencies=di)
)

# Mount Agnara HTTP app inside Starlette
# This allows calling /api/contact directly as an HTTP API if desired
starlette_app.mount("/", agnara_http)

app = starlette_app
