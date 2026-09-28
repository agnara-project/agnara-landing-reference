# Architecture

This project is built around the philosophy that **Agnara is the application runtime**, while other technologies act as hosts, adapters, or presentation layers.

## The Execution Graph

```mermaid
flowchart TD
    Browser[Browser]
    
    subgraph Host[Host Boundary]
        Starlette[Starlette Presentation Route]
        AgnaraHttp[agnara-http Runtime]
    end
    
    subgraph Agnara[Agnara Application Runtime]
        Bridge[Agnara Runtime Bridge]
        Runtime[CapabilityRuntime]
        Capability[Agnara Capability]
        DI[DIContainer]
    end
    
    subgraph Infra[Infrastructure Layer]
        Adapter[SqlAlchemy Adapter]
        SQLite[(SQLite)]
    end

    Browser -->|HTTP POST| Starlette
    Browser -->|HTTP POST| AgnaraHttp
    
    Starlette -->|Invocation| Bridge
    Bridge -->|ExecutionContext| Runtime
    AgnaraHttp -->|ExecutionContext| Runtime
    
    Runtime -->|Execute Plan| Capability
    Runtime -.->|Inject dependencies| DI
    DI -.->|Resolves| Adapter
    
    Capability -->|Uses Port| Adapter
    Adapter --> SQLite
```

## Direct Host Execution vs Native Agnara HTTP

The diagram above illustrates the two ways a capability is reached:

1. **Direct Host Execution**: A user visits the HTML landing page and submits a form. Starlette catches the POST, verifies CSRF, maps the payload into a plain Python dictionary, and passes it to the `Agnara Runtime Bridge`. The bridge constructs an `Invocation` and `ExecutionContext`, then calls `CapabilityRuntime.invoke_result()`.
2. **Native Agnara HTTP**: A client sends a POST to `/api/contact`. The request is intercepted by the ASGI application compiled by `agnara-http`. It binds the `FORM` payload to the capability's schema natively, constructs an `ExecutionContext`, and calls `CapabilityRuntime.invoke_result()`.

In both cases, execution semantics converge identically at the `CapabilityRuntime`. Validation, dependency injection, policies, and telemetry are enforced uniformly.
