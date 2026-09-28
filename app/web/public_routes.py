from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from starlette.routing import Route
from starlette.templating import Jinja2Templates

from app.web.security import generate_csrf_token, verify_csrf_token

templates = Jinja2Templates(directory="app/templates")


async def index(request: Request):
    csrf_token = generate_csrf_token(request)
    return templates.TemplateResponse(request, "index.html", {"csrf_token": csrf_token})


async def contact_post(request: Request):
    form = await request.form()

    # Security: Honeypot check
    if form.get("website_url"):  # The honeypot field
        return JSONResponse(
            {"status": "success", "message": "Message sent."}, status_code=200
        )

    # Security: CSRF verification
    csrf_token = form.get("csrf_token")
    if not csrf_token or not verify_csrf_token(request, str(csrf_token)):
        return JSONResponse(
            {
                "status": "error",
                "message": "Invalid CSRF token. Please refresh and try again.",
            },
            status_code=400,
        )

    # Extract fields
    name = str(form.get("name", ""))
    email = str(form.get("email", ""))
    message = str(form.get("message", ""))
    company = form.get("company")
    phone = form.get("phone")
    subject = form.get("subject")

    try:
        from app.capabilities.contacts import submit_contact

        # Call Agnara capability
        await submit_contact(
            name=name,
            email=email,
            message=message,
            company=company if company else None,
            phone=phone if phone else None,
            subject=subject if subject else None,
        )

        # If JS is disabled, redirect. Otherwise send JSON.
        if (
            request.headers.get("accept") == "application/json"
            or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        ):
            return JSONResponse(
                {
                    "status": "success",
                    "message": "Your message has been sent successfully!",
                }
            )
        else:
            return RedirectResponse(url="/?success=1", status_code=303)

    except ValueError as e:
        if request.headers.get("accept") == "application/json":
            return JSONResponse({"status": "error", "message": str(e)}, status_code=400)
        else:
            return RedirectResponse(url=f"/?error={str(e)}", status_code=303)
    except Exception:
        if request.headers.get("accept") == "application/json":
            return JSONResponse(
                {"status": "error", "message": "An internal error occurred."},
                status_code=500,
            )
        else:
            return RedirectResponse(url="/?error=internal", status_code=303)


routes = [
    Route("/", endpoint=index, methods=["GET"]),
    Route("/contact", endpoint=contact_post, methods=["POST"]),
]
