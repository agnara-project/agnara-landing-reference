# Project for Agents

This repository is optimized to be understood by AI Agents.

## What is this project?
An executable reference application demonstrating Agnara 1.0.3 as the application runtime. 

## Agnara-First Architecture

Agnara is not a library in this project. **It is the runtime.**

### What Agnara owns
* **Capability definitions**: The semantic operations of the application (`submit_contact`).
* **Execution plans**: Schemas, policies, and DI mappings.
* **Runtime invocation**: All execution happens through `CapabilityRuntime.invoke_result()`.
* **Dependency Injection**: `DIRegistry` handles dependency resolution.
* **Canonical outcomes**: Capabilities return `Success` or `Failure`.

### What Starlette owns
* HTTP presentation (Jinja2).
* Session authentication (login/logout).
* It creates a `Principal` identity and passes it to the `CapabilityRuntime`.

### What infrastructure owns
* Database models (SQLAlchemy).
* Repository implementations of application ports.

## Hard Rules (Never Break These)

1. **Application behavior belongs in Agnara capabilities.**
2. **Production web routes invoke capabilities through `CapabilityRuntime`.** Never import and call the Python handler directly to serve a web request.
3. **Web routes never call repository implementations.**
4. **Web routes never call capability handlers directly for application execution.** They must bridge via `app.runtime.invoke_capability`.
5. **Infrastructure implements application ports.** Capabilities depend on Protocols.
6. **Agnara DI resolves capability dependencies.** Do not pass Starlette state into DI.
7. **Raw host objects never enter capability inputs or Agnara DI.** No `Request` objects in capabilities.
8. **Admin authorization is enforced by Agnara scopes** in addition to host authentication. The host must construct a `Principal` from the session.
9. **Only public Agnara 1.0.3 APIs may be imported.** Never import `agnara._...` or `agnara_http._...`.
10. **Behavior changes require runtime-level tests.** Tests must construct a `CapabilityRuntime` and test through it.

## How to add a capability

1. Create a function in `app/apps/<context>/capabilities.py`.
2. Decorate it with `@app.capability()`. Declare `effects`, `risk`, and `scopes`.
3. Add any required repository ports to its signature.
4. If exposing via `agnara-http`, bind it in `app/main.py`.
5. Test it by invoking it through the `test_runtime` fixture.
