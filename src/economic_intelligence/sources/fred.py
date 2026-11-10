import json 
from datetime import datetime, timezone
import requests
from economic_intelligence.bronze import RawResponse

BASE_URL = "https://api.stlouisfed.org/fred"

def fetch_series_observations(
        series_id: str,
        api_key: str, 
        session: requests.Session | None = None, 
        timeout: float = 30, 
) -> RawResponse: 
    endpoint = "series/observations"
    params = {
        "series_id": series_id, 
        "file_type": "json"
    }
    http = session or requests.Session()
    response = http.get(f"{BASE_URL}/{endpoint}", params={**params, "api_key": api_key}, timeout=timeout)
    return RawResponse(
        source="fred", 
        endpoint=endpoint, 
        source_entity_id=series_id, 
        request_params=json.dumps(params, sort_keys=True), 
        http_status=response.status_code,
        payload=response.text,
        ingested_at=datetime.now(timezone.utc),
    )
