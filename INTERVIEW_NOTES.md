# Interview Notes

## 60–90 second project explanation

> I created a small ETL pipeline that retrieves hourly weather data for Athens from
> Open-Meteo. The extract layer supports both the live API and a bundled sample file,
> because I wanted the demo and tests to be deterministic even without network access.
> The transformation layer validates required fields, array lengths and business rules,
> and converts the source values into typed records. The load layer writes to PostgreSQL
> in a transaction and uses a composite key with `ON CONFLICT DO UPDATE`, so rerunning
> the pipeline does not create duplicates. I also added an audit table, structured logs,
> Docker Compose health checks, unit tests, SQL analytics and GitHub Actions CI. My
> strongest background is DevOps, so I deliberately focused on reliability,
> repeatability and observability around the data pipeline.

## The exact live demo

```bash
cp .env.example .env
make demo
make query
make demo
make query
```

Explain after the second run:

> The execution-history table gets a new run, but the weather table does not duplicate
> the business records because the load is idempotent.

Then show:

- `src/weather_etl/transform.py` for data-quality checks;
- `src/weather_etl/database.py` for transaction and upsert;
- `sql/analytics.sql` for CTEs, aggregation and `ROW_NUMBER()`;
- `docker-compose.yml` for the database health check;
- `.github/workflows/ci.yml` for lint and tests.

## Likely questions and concise answers

### Why ETL and not ELT?

The source is small and the validation and normalization rules are easy to express in
Python before loading. For warehouse-scale transformations, I would likely load raw data
first and use an ELT approach with SQL or dbt.

### Is the load incremental?

It is incremental at the business-key level. Every run receives a limited time window,
and the database inserts new timestamps or updates timestamps that already exist. A more
advanced historical pipeline would persist a watermark or use source-side change data.

### How is it idempotent?

`(location_name, observed_at)` is the primary key. The load uses `ON CONFLICT DO UPDATE`,
so the same input can be processed repeatedly without duplicate rows.

### What happens when bad data arrives?

The transformation layer raises a `DataQualityError` for missing fields, inconsistent
array lengths, null numeric values, invalid humidity and negative precipitation. The run
is recorded as failed with an error message.

### What happens when the API is temporarily unavailable?

The HTTP call has a timeout and fails the run. The next production improvement would be
bounded retries with exponential backoff and alerting. I would avoid infinite retries
because they can hide persistent failures and overload a dependency.

### Why did you not add Airflow?

The ETL is exposed as one repeatable command, so any scheduler can invoke it. Adding
Airflow only for a one-task demo would increase operational complexity. In production I
could schedule it with Airflow, a Kubernetes CronJob or another orchestrator.

### How would you handle larger volumes?

I would load into a staging table, use PostgreSQL `COPY` or bulk loading, process data in
chunks, partition by date, track a watermark, and move heavy transformations to a data
warehouse or distributed processing engine when the volume requires it.

### How would you manage secrets?

The repository contains only `.env.example`. Real credentials should come from CI/CD
secrets or a secrets manager and should never be committed to Git.

## SQL points to be ready to explain

- `WHERE` filters rows before aggregation; `HAVING` filters aggregated groups.
- `INNER JOIN` keeps matches; `LEFT JOIN` keeps all rows from the left side.
- A CTE makes a multi-step query easier to read and test.
- `ROW_NUMBER()` assigns a unique sequence within a partition and is useful for
  deduplication or selecting the latest row per entity.
- An index improves selected access patterns but adds storage and write overhead.
- A primary key enforces uniqueness and gives the upsert a conflict target.

## Be honest about the project

Say that this is a personal project built to consolidate and demonstrate ETL concepts.
Do not present it as a production system used by a previous employer. You can confidently
say that its operational choices reflect your real DevOps experience.
