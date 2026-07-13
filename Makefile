# --- Environment / dependencies ---
install:  ## Install dependencies with uv
	uv sync

pre-commit.install:  ## Install git hooks
	uv run pre-commit install

# --- Docker development ---
dev-up:  ## Build images and start all development services
	docker compose -f compose.dev.yml up -d --build

dev-down:  ## Stop all development services
	docker compose -f compose.dev.yml down

# --- Docker production ---
prod-up:  ## Build images and start all production services
	docker compose --env-file src/.env -f compose.prod.yml up -d --build

prod-down:  ## Stop all production services
	docker compose --env-file src/.env -f compose.prod.yml down

# --- Database migrations ---
migration.create:  ## Create migration: make migration.create name="migration name"
	docker compose -f compose.dev.yml run --rm backend alembic revision --autogenerate -m "$(name)"

migration.up:  ## Apply all migrations
	docker compose -f compose.dev.yml run --rm backend alembic upgrade head

migration.down:  ## Roll back one migration
	docker compose -f compose.dev.yml run --rm backend alembic downgrade -1

prod-migration.up:  ## Apply all production migrations
	docker compose --env-file src/.env -f compose.prod.yml run --rm backend alembic upgrade head

# --- Code quality ---
lint:  ## Format, lint, and type-check
	uv run ruff format src/
	uv run ruff check src/ --fix
	uv run mypy src/
