"""stegdb_wirein.py - Production StegDB client."""
import requests
from typing import Dict, Any, Optional

class StegDBClient:
    def __init__(self, base_url: str = "https://stegdb.stegverse.org", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"

    def log_action(self, action_type: str, receipt_id: str, data: Dict[str, Any]) -> bool:
        try:
            resp = self.session.post(f"{self.base_url}/v1/log", json={"action_type": action_type, "receipt_id": receipt_id, "data": data}, timeout=10)
            return resp.status_code == 200
        except Exception as e:
            print(f"[StegDB] Log failed: {e}")
            return False

    def query_gate(self, manifest_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            resp = self.session.post(f"{self.base_url}/v1/gate/evaluate", json=manifest_data, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            return {"result": "FAIL_CLOSED", "confidence": 1.0, "reasoning": f"StegDB error: {resp.status_code}"}
        except Exception as e:
            return {"result": "FAIL_CLOSED", "confidence": 1.0, "reasoning": f"StegDB unreachable: {e}"}

    def get_repo_state(self, repo: str) -> Dict[str, Any]:
        try:
            resp = self.session.get(f"{self.base_url}/v1/repos/{repo}", timeout=10)
            return resp.json() if resp.status_code == 200 else {}
        except:
            return {}
