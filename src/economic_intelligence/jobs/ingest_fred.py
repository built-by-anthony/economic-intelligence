import argparse
import uuid 

from databricks.sdk import WorkspaceClient

from economic_intelligence.bronze import append_raw_response
from economic_intelligence.sources.fred import fetch_series_observations
from economic_intelligence.spark import get_spark

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--series", nargs="+", default=["UNRATE"])
    args = parser.parse_args(argv)

    spark = get_spark()
    api_key = WorkspaceClient().dbutils.secrets.get(scope="economic-intelligence", key="fred-api-key")
    run_id = str(uuid.uuid4())

    responses = [fetch_series_observations(s, api_key) for s in args.series]
    table = f"{args.catalog}.{args.schema}.raw_api_responses"
    n = append_raw_response(spark, table, responses, run_id)

    written = spark.table(table).where(f"ingestion_run_id = '{run_id}'").count()
    if written != len(args.series):
        raise RuntimeError(f"run {run_id}: expected {len(args.series)} rows, found {written} in {table}")

    failed = [r.source_entity_id for r in responses if r.http_status != 200]
    if failed:
        raise RuntimeError(f"run {run_id}: non-200 responses for {failed}")

    print(f"run {run_id}: wrote {n} rows to {table}")

if __name__ == "__main__":
    main()