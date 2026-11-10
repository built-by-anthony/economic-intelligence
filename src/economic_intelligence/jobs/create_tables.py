import argparse
from importlib.resources import files

from economic_intelligence.spark import get_spark

DDL_FILES = ["bronze/raw_api_responses.sql"]

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--schema", required=True)
    args = parser.parse_args(argv)

    spark = get_spark()
    sql_dir = files("economic_intelligence") / "sql"

    for path in DDL_FILES:
        statement = (sql_dir / path).read_text()
        spark.sql(statement, args={"catalog": args.catalog, "schema": args.schema})
        print(f"applied {path} to {args.catalog}.{args.schema}")

if __name__ == "__main__":
    main()