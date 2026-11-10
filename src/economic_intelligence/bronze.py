from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass(frozen=True)
class RawResponse:
    source: str
    endpoint: str
    source_entity_id: str | None
    request_params: str
    http_status: int
    payload: str
    ingested_at: datetime

def append_raw_response(spark, table: str, responses: list[RawResponse], run_id: str) -> int: 
    rows = []
    for r in responses:
        row = asdict(r)
        row["ingestion_run_id"] = run_id
        rows.append(row)
        df = spark.createDataFrame(rows, schema=spark.table(table).schema)
        df.write.mode("append").saveAsTable(table)
        return len(rows)