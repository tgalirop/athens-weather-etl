.PHONY: help build demo live query test lint down reset logs

help:
	@echo "make demo   - run deterministic ETL with bundled sample data"
	@echo "make live   - run ETL against the live Open-Meteo API"
	@echo "make query  - execute analytics SQL"
	@echo "make test   - run unit tests"
	@echo "make lint   - run Ruff checks"
	@echo "make reset  - remove containers and database volume"

build:
	docker compose build

demo:
	SOURCE_MODE=sample docker compose up --build --abort-on-container-exit etl

live:
	SOURCE_MODE=live docker compose up --build --abort-on-container-exit etl

query:
	docker compose up -d postgres
	docker compose exec -T postgres psql -U weather -d weather -f /dev/stdin < sql/analytics.sql

test:
	docker build -t athens-weather-etl:test .
	docker run --rm --entrypoint sh athens-weather-etl:test -c "pip install --no-cache-dir '.[dev]' >/dev/null && pytest -q"

lint:
	docker build -t athens-weather-etl:test .
	docker run --rm --entrypoint sh athens-weather-etl:test -c "pip install --no-cache-dir '.[dev]' >/dev/null && ruff check src tests"

logs:
	docker compose logs -f

down:
	docker compose down

reset:
	docker compose down -v --remove-orphans
