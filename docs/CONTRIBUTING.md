# Contributing & Coding Conventions

## Repository conventions

- Monorepo layout: `/apis`, `/services`, `/infra`, `/docs`, `/deploy`.
- API-first: change the OpenAPI contract in `/apis` before implementing.
- One ADR per significant decision in `docs/adr/`.

## Python (Payment Initiation, rail adapters, tooling)

- Python 3.12.
- **4-space indentation** (enforced by `.editorconfig` and Ruff).
- **Docstrings on all functions** (module, class, and function level).
- **Type hints** on all function parameters and return values.
- Prefer **f-strings** over `.format()` or `%` formatting.
- Keep **functions under 30 lines** where possible.
- Tooling: `ruff` (lint + format), `mypy` (types), `pytest` (tests).
- Dependency/venv management: `uv` (or `pip` + `venv`).

## C# / .NET (Payment Order, Payment Execution)

- .NET 8 (LTS).
- 4-space indentation, file-scoped namespaces, nullable reference types enabled.
- xUnit for tests.
- One aggregate per bounded context; domain events are immutable records.

## Terraform (infra)

- 2-space indentation.
- Reusable modules under `infra/modules`, environments under `infra/environments`.
- `terraform fmt` and `terraform validate` must pass.

## Commits & branches

- Never commit secrets (`.env`, credentials). See `.gitignore`.
- Feature branches; PRs run lint + tests + contract validation.
