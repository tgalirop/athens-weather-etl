# Architecture

```mermaid
flowchart LR
    A[Open-Meteo API or sample JSON] --> B[Extract]
    B --> C[Transform and data-quality checks]
    C --> D[PostgreSQL upsert]
    D --> E[Analytics SQL]
    F[Docker Compose] -. runtime .-> B
    F -. runtime .-> D
    G[GitHub Actions] -. lint and tests .-> C
```

The pipeline is intentionally small, but it demonstrates production-oriented ideas:

- deterministic local execution with sample data;
- a live API mode;
- schema constraints and application-level quality checks;
- idempotent loading through a composite primary key and `ON CONFLICT`;
- an ETL run audit table;
- container health checks and CI.
