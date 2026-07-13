# InfoCity Semantic Search

FastAPI service for semantic search over question-answer pairs from a prepared
CSV file. PostgreSQL with pgvector stores embeddings and search statistics,
while Celery and Redis handle background indexing.

## Development

```bash
cp src/.env.example src/.env
make dev-up
make migration.up
```

Open Swagger UI at <http://localhost:8000/docs> and call
`POST /api/sources/indexing` to index `data/questions.csv`.

Stop the services with `make dev-down`.

## Production

Configure `src/.env`, including `HTTP_PROXY` and `HTTPS_PROXY` when required,
then run:

```bash
make prod-up
make prod-migration.up
```

The production image is built with the corporate proxy required by the task.
Stop it with `make prod-down`.

## Useful commands

```text
make install             Install local dependencies
make pre-commit.install  Install Git hooks
make migration.create name="migration name"
make migration.down      Roll back one development migration
make lint                Format, lint, and type-check the code
```
