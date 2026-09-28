import os
from contextlib import asynccontextmanager

from agnara import Agnara
from agnara.core.di import DIContainer
from agnara.di import DIRegistry, provider
from agnara.execution import CapabilityRuntime, ExecutionPlan
from agnara_http import (
    Binding,
    BindingSource,
    Http,
    HttpDocumentation,
    HttpExplorer,
    OpenApiInfo,
)
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.staticfiles import StaticFiles

from app.apps.contacts.app import app as contacts_app
from app.apps.contacts.capabilities import submit_contact
from app.apps.contacts.ports import ContactRepository
from app.infrastructure.persistence.database import AsyncSessionLocal, init_db
from app.infrastructure.persistence.repositories import SqlAlchemyContactRepository
from app.settings import settings
from app.web.admin_routes import routes as admin_routes
from app.web.auth import routes as auth_routes
from app.web.public_routes import routes as public_routes
from app.web.security import SecurityHeadersMiddleware

# 1. Bounded Contexts
project = Agnara("agnara_site")
project.include(contacts_app)

# 2. Compile Capabilities
capabilities = project.compile()

# 3. Compile DI
dependencies = DIRegistry()


@provider()
def provide_repo() -> ContactRepository:
    return SqlAlchemyContactRepository(AsyncSessionLocal)


dependencies.bind(ContactRepository, provide_repo)

# 4. Compile Execution Plans
plans = tuple(
    ExecutionPlan.compile(
        capabilities[capability_id],
        dependencies,
    )
    for capability_id in capabilities
)

# 5. Global Runtime instances
container = DIContainer(dependencies)
runtime = CapabilityRuntime(
    capabilities,
    plans,
    container,
)

# 6. HTTP API (agnara-http)
api = (
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
    .compile(
        capabilities,
        dependencies=dependencies,
        openapi=OpenApiInfo(title="Agnara API", version="1.0.0"),
        documentation=HttpDocumentation(),
    )
)


# 7. Lifecycle
@asynccontextmanager
async def lifespan(app: Starlette):
    await init_db()
    # Attach runtime to app state
    app.state.agnara_runtime = runtime
    yield
    # Cleanup
    await runtime.aclose()
    await container.aclose()


# 8. Web Routes (Presentation Boundary)
middleware = [
    Middleware(
        SessionMiddleware,
        secret_key=settings.SESSION_SECRET,
        https_only=settings.SECURE_COOKIES,
        same_site="lax",
    ),
    Middleware(SecurityHeadersMiddleware),
]


async def health_check(request):
    return JSONResponse({"status": "ok"})


routes = [
    Route("/health", endpoint=health_check, methods=["GET"]),
]
routes.extend(public_routes)
routes.extend(auth_routes)
routes.extend(admin_routes)

# 9. Host Assembly
app = Starlette(
    debug=settings.DEBUG,
    routes=routes,
    middleware=middleware,
    lifespan=lifespan,
)

if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Mount API
app.mount("/", api)
