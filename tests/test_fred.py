import json 

from economic_intelligence.sources.fred import fetch_series_observations

class FakeResponse:
    status_code = 200
    text = '{"observations": []}'

class FakeSession: 
    def __init__(self):
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append({
            "url": url,
            "params": params
        })
        return FakeResponse()

def test_api_key_is_sent_but_not_stored():
    session = FakeSession()

    resp = fetch_series_observations("UNRATE", api_key = "test-key", session=session)
    sent_params = session.calls[0]["params"]
    assert sent_params["api_key"] == "test-key"
    assert "api_key" not in json.loads(resp.request_params)
