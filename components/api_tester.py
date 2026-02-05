import requests
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class TestResult:
    success: bool
    status_code: int
    latency_ms: float
    response_data: Optional[Dict[str, Any]]
    error_message: str
    raw_response: str

class APITester:
    def __init__(self, endpoint_url: str, api_key: str, timeout: int = 15):
        self.endpoint_url = endpoint_url.strip()
        self.api_key = api_key.strip()
        self.timeout = timeout

    def build_headers(self):
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": self.api_key
        }

    def build_payload(self, audio_base64: str, language: str):
        return {
            "language": language,
            "audio_format": "mp3",
            "audio_base64": audio_base64.strip()
        }

    def get_result(self, audio_base64: str, language: str = "auto"):
        start = time.perf_counter()

        try:
            res = requests.post(
                self.endpoint_url,
                json=self.build_payload(audio_base64, language),
                headers=self.build_headers(),
                timeout=self.timeout
            )

            latency = (time.perf_counter() - start) * 1000

            try:
                data = res.json()
            except:
                data = None

            return TestResult(
                success=200 <= res.status_code < 300,
                status_code=res.status_code,
                latency_ms=round(latency, 2),
                response_data=data,
                error_message="",
                raw_response=res.text
            )

        except Exception as e:
            return TestResult(
                success=False,
                status_code=0,
                latency_ms=0,
                response_data=None,
                error_message=str(e),
                raw_response=""
            )
