# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

Economic Intelligence Lakehouse: a learning project for Databricks (Free Edition) that ingests public economic data (FRED first; later BLS, BEA, Census) through a Bronze → Silver → Gold medallion architecture.

**`claude_handoff_economic_intelligence.md` is the authoritative project brief.** Read it for the full data model, milestones, proposed repo layout, and initial FRED series list before proposing structure. Its proposed repo tree is only a sketch; check what actually exists.

## Databricks layout

- Workspace: Free Edition, `https://dbc-21474648-f078.cloud.databricks.com`, CLI profile `DEFAULT` (OAuth).
- Catalog `economic_intelligence` was created once by hand in SQL and is deliberately **not** managed by the bundle, so `bundle destroy` can't remove it.
- The bundle (`databricks.yml` + `resources/*.yml`) manages the `bronze`/`silver`/`gold` schemas. The `dev` target uses `mode: development`, which prefixes names: deployed schemas are `economic_intelligence.dev_anthony_{bronze,silver,gold}`. A future `prod` target gets unprefixed names. Code must therefore take catalog/schema as parameters (bundle variables / job parameters), never hardcode them.
- Commands: `databricks bundle validate`, `databricks bundle summary` (shows resolved names), `databricks bundle deploy`, `databricks bundle run fred_ingestion`.
- `${resources.*}` references (e.g. `${resources.schemas.bronze.name}` in the job parameters) resolve only at deploy; `validate` shows them literally. Check the deployed job with `databricks jobs get <id>`.
- Naming: hyphens for labels (bundle name, pyproject distribution name, secret scope `economic-intelligence`); underscores for Unity Catalog names and the Python import name (`economic_intelligence`).

## Code layout and execution

- Installable package under `src/economic_intelligence/` (`pip install -e .`). Source modules (`sources/fred.py`) return `RawResponse` objects and never touch Spark; `bronze.py` writes them to `<catalog>.<schema>.raw_api_responses` in one append commit per run. New sources add a module under `sources/` without changing the writer.
- Entry point `ingest_fred` (`[project.scripts]` in `pyproject.toml`) takes `--catalog --schema --series ...`. `get_spark()` uses Databricks Connect locally and the built-in session in jobs.
- Local runs go to serverless through Databricks Connect (profile `dbc-21474648-f078` has `serverless_compute_id = auto`): `python -m economic_intelligence.jobs.ingest_fred --catalog economic_intelligence --schema dev_anthony_bronze`. The VS Code Databricks extension works on Free Edition serverless.
- The bundle `artifacts` section builds the wheel (`dynamic_version: true` so serverless doesn't reuse a cached `0.1.0`); `resources/fred_ingestion.job.yml` runs it as a `python_wheel_task` on serverless environment version 4.
- Every subpackage needs an `__init__.py`: setuptools `packages.find` silently drops folders without one, so the wheel would miss modules that still import fine locally.
- Free Edition: public DBFS root is disabled (`dbutils.fs.ls("/")` fails); use Unity Catalog volumes for files. Local `WorkspaceClient().dbutils` only supports `fs` and `secrets`; anything else (including a typo) fails with a misleading `cluster_id is required`.
- Tests: `pytest -v`; single test: `pytest tests/test_fred.py::test_api_key_is_sent_but_not_stored`. Tests stub the HTTP session and never hit the network.

## How the user wants to work

The user (Tony) is learning Databricks by building this and writes the code themselves. These preferences come from the handoff doc:

- Work incrementally: give the next small set of steps, then wait for the user's output before assuming success. Don't assume earlier-suggested installs or signups were done.
- Explain what each command or component does and why, especially Databricks-specific concepts (Unity Catalog, Delta, Lakeflow, bundles). The user already knows Python, PostgreSQL, Docker, and API ingestion.
- No large code dumps; build a thin working slice first.
- Separate verified facts from assumptions. Databricks Free Edition limits and CLI syntax change — check current official docs before relying on a feature (outbound network access, Unity Catalog permissions, bundles/"Declarative Automation Bundles", Lakeflow Declarative Pipelines).
- Use both SQL and Python; don't make everything a Python notebook.
- No Docker, PostgreSQL, or other cloud providers in the initial phase.

## Secrets

The user has a FRED API key. Never ask them to paste it in chat and never hardcode it. Use an environment variable locally (`.env` is gitignored) and Databricks secrets in the workspace.

## Local Python environment

- Use `.venv` (Homebrew `python@3.12`). Don't touch `/usr/bin/python3` (system 3.9.6), global symlinks, or global `PATH`.
- Activate: `source .venv/bin/activate`
- The doubled `((.venv) )` prompt is cosmetic: the generated `.venv/bin/activate` wraps an already-parenthesized prompt in a second pair. It is not caused by `~/.zshrc`; the environment itself has been verified correct.
- Dev-only deps (Databricks Connect, pytest) are in `requirements-dev.txt`; never put `databricks-connect` in the package's runtime dependencies.

## Architectural invariants

- **Bronze** keeps raw API payloads with ingestion timestamp and source metadata, appended (ingestion history, never overwrite the only copy). **Silver** normalizes dates/units/frequency/geography, deduplicates (Delta `MERGE`), validates, and keeps source identifiers. **Gold** holds curated analytical tables.
- Revisions and vintages are a core goal (ALFRED for FRED). Keep four dates distinct: observation date (period described), release date (source publication), ingestion timestamp (our fetch), and vintage date (as-of version of the value).
- Ingestion must be source-agnostic enough that adding BLS/BEA/Census doesn't require rewriting the platform.
- If the Databricks workspace can't reach an API, the fallback is to ingest from the Mac and upload the raw files. Test FRED connectivity from the workspace early.
