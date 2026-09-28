# Agnara Architectural Audit

This document traces exactly how Agnara 1.0.3 components are used in this reference application.

## 1. App Model
We define `App("contacts")` in `app/apps/contacts/app.py`. This groups the domain boundaries natively.

## 2. Capabilities
Capabilities (`submit`, `list`, `get`, `update_status`, `dashboard`) are defined using `@app.capability()` and they include metadata like `Risk`, `StandardEffect`, `scopes`, and `idempotent`.

## 3. Composition Root & Frozen Registry
In `app/main.py`, the global `Agnara("agnara_site")` includes the `contacts` app and compiles it into a `FrozenCapabilityRegistry`.

## 4. Execution Plans
The `FrozenCapabilityRegistry` is iterated over, and `ExecutionPlan.compile(definition, dependencies)` is called for each to build static execution paths.

## 5. Dependency Injection
`DIRegistry()` is instantiated in `app/main.py`. The `@provider()` decorator is used to map `ContactRepository` to `SqlAlchemyContactRepository`. A global `DIContainer` holds this registry.

## 6. CapabilityRuntime
`CapabilityRuntime` is initialized with the capabilities, plans, and DI container. It is attached to the Starlette application state to serve as the unified execution boundary.

## 7. Bridge (Invocation, ExecutionContext, Principal)
`app/runtime.py` creates a bridge for Starlette routes. It builds an `Invocation` from the HTTP payload, sets up an `ExecutionContext`, handles `AnonymousPrincipal` or a scoped `Principal`, and calls `runtime.invoke_result()`.

## 8. Canonical Outcomes
Starlette routes check `isinstance(result, Failure)` and `isinstance(result, Success)` to determine HTTP status codes and responses.

## 9. Agnara HTTP
`agnara-http` compiles a native HTTP API using `Http("api").post(...)`, mapping `BindingSource.FORM` directly to the `submit` capability.

## 10. OpenAPI
`OpenApiInfo` and `HttpDocumentation` generate an OpenAPI specification and serve a Swagger UI at `/api/docs`.
