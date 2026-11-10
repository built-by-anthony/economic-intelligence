import argparse
import uuid 

from databricks.sdk import WorkspaceClient

from economic_intelligence.bronze import append_raw_response
from economic_intelligence.sources.fred import fetch_series_observations

def get_spark():
    try:
        from databricks.connect import DatabricksSession
        return DatabricksSession.builder.getOrCreate()
    except ImportError:
        from pyspark.sql import SparkSession
        return SparkSession.builder.getOrCreate()

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
    print(f"run {run_id}: wrote {n} rows to {table}")

if __name__ == "__main__":
    main()