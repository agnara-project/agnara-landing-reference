# Agnara Core Integration

This document clarifies exactly where and how Agnara is used in this project.

## Responsibilities

**Agnara Controls:**
- Capability definitions (the use cases of the application).
- Dependency Injection (wiring repositories into capabilities).
- Business operations and validation.
- HTTP capability exposure (via `agnara-http`).

**Other Libraries:**
- **Jinja2**: Renders HTML templates for the browser.
- **Starlette**: Acts as the ASGI host, composing static files, sessions, and the web routes.
- **SQLAlchemy**: An infrastructure adapter to handle persistence.
- **SQLite**: The storage engine.
- **Uvicorn**: The ASGI server running the application.

## Example Flow

When a user submits the contact form:
1. Starlette receives the `POST /contact` request.
2. The route handler validates the CSRF token and extracts form data.
3. The route handler retrieves the `submit_contact` capability from the Agnara `App` instance.
4. The capability is executed. Agnara automatically injects the registered `ContactRepository`.
5. The capability validates the input and calls the repository.
6. The repository (implemented via SQLAlchemy) saves the data to SQLite.
7. The capability returns the domain model to the route handler.
8. Starlette returns a JSON or Redirect response.
