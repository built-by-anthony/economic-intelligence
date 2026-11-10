# Claude Handoff: Economic Intelligence Lakehouse

## Purpose of this document

This document gives you the context needed to continue helping me build
a Databricks learning project without making me repeat the background.
Treat it as the working project brief and current-state handoff. I am
learning as I build, so explain decisions and proceed incrementally
rather than dumping a large amount of code at once.

## 1. Project overview

I am building an **Economic Intelligence Lakehouse**: a production-style
data platform for public economic data. The goal is to learn Databricks
and modern data engineering by building a real, extensible data
product---not just a dashboard or tutorial exercise.

The platform will ingest public data from sources such as:

-   FRED (Federal Reserve Economic Data)
-   BLS (Bureau of Labor Statistics)
-   BEA (Bureau of Economic Analysis)
-   US Census Bureau

The long-term goal is to create a trusted, standardized historical data
asset with observations, metadata, update history, release dates,
revisions, and historical vintages. It should eventually support
economic analysis, dashboards, and forecasting.

Questions the platform may eventually help answer:

-   Is inflation accelerating or decelerating?
-   Are labor market conditions deteriorating?
-   How do interest rates relate to unemployment and GDP growth?
-   Which indicators tend to lead recessions?
-   How do economic conditions differ across US states?
-   What did we know about the economy at a particular point in time?

An important feature is **revision/vintage tracking**. Economic
statistics are often revised after initial publication. I want to
preserve what was known at different points in time, not just overwrite
old values with the latest values. FRED's ALFRED service is relevant for
historical vintage data.

## 2. Intended architecture

Use a medallion architecture:

### Bronze --- raw source data

-   Preserve raw API responses and source payloads.
-   Record ingestion timestamps and source metadata.
-   Keep ingestion history rather than overwriting the only copy.
-   Initially ingest FRED data.

### Silver --- standardized data

-   Normalize observation dates, units, frequencies, geography, series
    identifiers, and missing values.
-   Deduplicate and validate observations.
-   Establish consistent schemas across source systems.
-   Preserve source-specific identifiers and metadata.

### Gold --- analytical products

-   Curated datasets for economic analysis.
-   Inflation, labor market, recession-monitoring, and regional-economy
    datasets.
-   Data suitable for Databricks SQL dashboards and downstream models.

### Consumption

-   Databricks SQL and dashboards
-   Python/PySpark notebooks
-   Eventually forecasting and machine-learning workflows

## 3. Candidate data model

Potential tables discussed so far:

  Table                      Purpose
  -------------------------- ----------------------------------------------------
  `dim_indicator`            Indicator definitions, names, units, and frequency
  `dim_source`               Source systems and API information
  `dim_geography`            Country, state, county, and metro-area metadata
  `dim_date`                 Calendar/reporting periods
  `fact_observation`         Standardized economic indicator observations
  `fact_revisions`           Historical changes to observations
  `fact_releases`            Publication and release dates
  `pipeline_execution_log`   Ingestion history and execution status

Potential observation attributes:

-   `indicator_id`
-   `observation_date`
-   `value`
-   `ingested_at`
-   `release_date`
-   `vintage_date`
-   `source_series_id`
-   `unit_of_measure`
-   `frequency`
-   `seasonal_adjustment`
-   source identifier / lineage fields

Keep these dates conceptually distinct: - **Observation date:** the
period the statistic describes. - **Release date:** when the source
published the statistic. - **Ingestion timestamp:** when our pipeline
retrieved it. - **Vintage date:** the version/as-of date associated with
the value.

Do not treat illustrative values in earlier notes as verified current
data.

## 4. Initial FRED scope

Start with these seven FRED series:

  FRED ID      Indicator                Frequency
  ------------ ------------------------ -----------
  `GDP`        Nominal GDP              Quarterly
  `GDPC1`      Real GDP                 Quarterly
  `UNRATE`     Unemployment rate        Monthly
  `CPIAUCSL`   Consumer Price Index     Monthly
  `FEDFUNDS`   Federal funds rate       Monthly
  `DGS10`      10-year Treasury yield   Daily
  `PAYEMS`     Total nonfarm payrolls   Monthly

Primary FRED observations endpoint:

`https://api.stlouisfed.org/fred/series/observations`

Typical parameters: - `series_id` - `api_key` - `file_type=json` -
`observation_start` - `observation_end`

Initial approach: retrieve the available historical observations for
each series. Later, implement incremental ingestion and
ALFRED/vintage-aware revision tracking.

I already obtained a FRED API key. **Never ask me to paste the key into
chat or hardcode it in source code.** Help me store it safely using an
environment variable locally and/or Databricks secrets when appropriate.

## 5. Databricks learning goals

I want to learn the Databricks ecosystem by using it in this project:

-   Apache Spark / PySpark
-   Delta Lake
-   Unity Catalog
-   Databricks Workflows / Lakeflow Jobs
-   Lakeflow Declarative Pipelines, where available
-   Databricks SQL
-   Data quality checks / expectations
-   MLflow
-   Databricks dashboards
-   Eventually CI/CD and deployment practices

Use both Python and SQL. Do not turn the entire project into Python
notebooks.

I intend to start with **Databricks Free Edition**. Be careful not to
overstate feature availability: Free Edition has resource and feature
limitations, and product capabilities can change. Verify current
documentation when a decision depends on current Free Edition behavior.

A key possible constraint is outbound network access from the workspace.
FRED/BLS/BEA/Census endpoints may not all be reachable. Test FRED
connectivity early. If the workspace cannot reach the API, run ingestion
from my Mac and upload the resulting raw files to Databricks.

Do not introduce Docker, PostgreSQL, or another cloud provider at the
beginning. Keep the initial focus on Databricks.

## 6. Development environment and repository

I am developing on macOS.

My previously reported versions: - Homebrew `7.0.13` - Git
`2.50.1 (Apple Git-155)` - Apple's/system `python3` was `3.9.6`

The setup plan was to install a separate Homebrew-managed Python 3.12,
without replacing or modifying Apple's `/usr/bin/python3`, then create a
project-local virtual environment.

Recommended commands:

``` bash
brew install python@3.12
```

Find the Homebrew installation prefix:

``` bash
brew --prefix python@3.12
```

Invoke that interpreter explicitly:

``` bash
"$(brew --prefix python@3.12)/bin/python3.12" --version
```

From the project root, create the virtual environment using that exact
interpreter:

``` bash
"$(brew --prefix python@3.12)/bin/python3.12" -m venv .venv
```

Activate it:

``` bash
source .venv/bin/activate
```

Verify:

``` bash
echo "$VIRTUAL_ENV"
which python
python --version
```

Expected: - `VIRTUAL_ENV` points to the project's `.venv`. -
`which python` points to `<project-root>/.venv/bin/python`. - Python
reports version `3.12.x`.

Deactivate with:

``` bash
deactivate
```

Do not modify `/usr/bin/python3`, create global Python symlinks, or
change global `PATH` just to make this project work. Keep system Python,
Homebrew Python, and the project virtual environment separate.

### Current terminal prompt issue

After activating the environment, my prompt appeared as:

``` text
((.venv) ) tony@Tonys-MacBook-Pro economic-intelligence %
```

instead of the usual:

``` text
(.venv) tony@Tonys-MacBook-Pro economic-intelligence %
```

This may simply be a duplicate virtual-environment indicator caused by
the shell prompt configuration already displaying the environment name
while Python's activation script adds it again. It is not, by itself,
proof that the environment is broken.

**Current immediate task:** ask me to run and share the output of:

``` bash
echo "$VIRTUAL_ENV"
which python
python --version
```

Use those results to verify the environment before changing shell
configuration. Do not immediately tell me to reinstall Python or edit
`.zshrc`. If the interpreter and environment paths are correct, explain
that the odd prompt is cosmetic and optionally help remove the duplicate
indicator after confirming which shell/prompt setup I use.

### Proposed repository structure

``` text
economic-intelligence/
├── databricks.yml
├── resources/
│   ├── fred_ingestion.job.yml
│   └── economic_pipeline.pipeline.yml
├── src/
│   ├── ingestion/
│   │   ├── fred_client.py
│   │   └── ingest_series.py
│   ├── transformations/
│   │   ├── bronze_to_silver.py
│   │   └── silver_to_gold.py
│   └── notebooks/
│       └── 01_fred_ingestion.py
├── sql/
│   └── 01_create_schemas.sql
├── tests/
│   └── test_fred_client.py
├── .gitignore
└── README.md
```

A possible initial `.gitignore`:

``` gitignore
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.env
.env.*
!.env.example
.databricks/
.DS_Store
*.log
```

Potential initial dependencies: - `requests` - `pytest`

Potential initial virtual environment setup:

``` bash
python -m pip install --upgrade pip
pip install requests pytest
```

### Databricks Asset Bundles

The project may use Databricks Declarative Automation Bundles (formerly
Databricks Asset Bundles) for workspace resources and deployment. Verify
current CLI syntax and Free Edition compatibility before relying on it.

An initial minimal `databricks.yml` draft was:

``` yaml
bundle:
  name: economic-intelligence

targets:
  dev:
    mode: development
    default: true
```

Do not assume this configuration is complete or valid for every current
CLI/Free Edition version; validate it with the installed CLI.

An initial SQL draft was:

``` sql
CREATE CATALOG IF NOT EXISTS economic_intelligence;
CREATE SCHEMA IF NOT EXISTS economic_intelligence.bronze;
CREATE SCHEMA IF NOT EXISTS economic_intelligence.silver;
CREATE SCHEMA IF NOT EXISTS economic_intelligence.gold;
```

Check actual Unity Catalog permissions and Free Edition behavior before
running it.

## 7. Planned milestones

### Milestone 1 --- FRED ingestion / Bronze

-   Confirm FRED API access and credentials.
-   Create or confirm Databricks Free Edition workspace.
-   Create the project catalog/schemas if supported.
-   Create the first notebook.
-   Ingest the seven initial FRED series.
-   Preserve raw API responses in Bronze Delta tables.
-   Build reusable ingestion functions.
-   Add basic ingestion logging and tests.

### Milestone 2 --- Silver data engineering layer

-   Standardize observations and metadata.
-   Build the dimensional model.
-   Add data quality checks.
-   Implement deduplication and Delta `MERGE` where appropriate.
-   Track revisions and historical vintages.
-   Add BLS and BEA as additional sources.

### Milestone 3 --- Productionization

-   Schedule workflows.
-   Add retries and error handling.
-   Add pipeline monitoring and execution logs.
-   Track lineage.
-   Implement source-specific incremental ingestion.

### Milestone 4 --- Gold analytical products

-   Create curated Gold tables.
-   Build inflation and labor-market dashboards.
-   Build recession-monitoring indicators.
-   Add regional comparisons.
-   Experiment with forecasting and recession prediction.
-   Track experiments/models with MLflow.

## 8. Longer-term analytical products

Potential products: 1. **Inflation Intelligence:** CPI, PCE, PPI, wage
growth, inflation expectations; month-over-month and year-over-year
changes. 2. **Labor Market Monitor:** unemployment, job openings, quits,
payrolls, labor-force participation, wage growth. 3. **Recession Early
Warning System:** yield curve, unemployment claims, industrial
production, leading indicators. 4. **Regional Economic Intelligence:**
GDP, wages, employment, population, and housing across states and metro
areas.

These are future goals, not immediate scope. Do not let them distract
from getting the first FRED-to-Bronze pipeline working.

## 9. How I want you to help

Please follow these collaboration preferences:

1.  **Work incrementally.** Give me the next small set of steps, then
    wait for my output before assuming they succeeded.
2.  **Teach, don't just prescribe.** Explain what each command or
    component does and why we are using it.
3.  **Be technically precise.** Distinguish verified facts from
    assumptions. If a Databricks Free Edition feature or CLI command may
    have changed, check current official documentation.
4.  **Do not assume state.** I may not have completed an installation or
    signup just because it was previously suggested.
5.  **Avoid unnecessary complexity.** Build a working thin slice first,
    then expand.
6.  **Protect secrets.** Never ask me to share my FRED API key. Use safe
    secret handling.
7.  **Preserve architectural intent.** Keep raw source data, standardize
    it in Silver, and create analytical products in Gold. Design
    ingestion so another source can be added without rewriting the
    platform.
8.  **Use my existing Python knowledge as a bridge**, but explain
    Databricks-specific concepts. I have prior experience with Python,
    PostgreSQL, Docker, and API ingestion projects, but I am
    specifically trying to learn Databricks here.
9.  **Do not overwhelm me with a giant implementation.** Explain one
    concept at a time and let me run commands and report results.

## 10. Exact next step

Continue from the current macOS virtual-environment verification.

Ask me to run:

``` bash
echo "$VIRTUAL_ENV"
which python
python --version
```

Then interpret the output. If the virtual environment is correct,
reassure me that the doubled `((.venv) )` prompt is likely cosmetic and
help clean it up only if I want to. Once the local Python setup is
verified, continue with the remaining prerequisites and Databricks
workspace setup, checking what I have actually completed.

The overall project goal remains: build a reusable, production-style
Economic Intelligence Lakehouse, starting with seven FRED series and a
Bronze → Silver → Gold architecture on Databricks Free Edition.
