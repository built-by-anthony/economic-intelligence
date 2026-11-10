CREATE TABLE IF NOT EXISTS economic_intelligence.dev_anthony_bronze.raw_api_responses (
  ingestion_run_id  STRING    NOT NULL COMMENT 'Groups all calls from one pipeline run',
  source            STRING    NOT NULL COMMENT 'Source system, e.g. fred',
  endpoint          STRING    NOT NULL COMMENT 'API path, e.g. series/observations',
  source_entity_id  STRING             COMMENT 'Source identifier requested, e.g. FRED series_id',
  request_params    STRING             COMMENT 'Request parameters as JSON, credentials removed',
  http_status       INT                COMMENT 'HTTP status code returned',
  payload           STRING             COMMENT 'Raw response body, unparsed',
  ingested_at       TIMESTAMP NOT NULL COMMENT 'When our pipeline received the response'
)
COMMENT 'Append-only log of raw API responses from all sources';