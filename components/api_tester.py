"""
API Tester Module - Core Testing Logic
Enhanced with conditional payload (URL/Base64) and language support
"""
import requests
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TestResult:
    """Data class to hold test results"""
    success: bool
    status_code: int
    latency_ms: float
    response_data: Optional[Dict[str, Any]]
    error_message: str
    raw_response: str


class APITester:
    """
    Core API Tester class for testing AI Voice Detection APIs
    Enhanced with URL/Base64 modes and language support
    """
    
    def __init__(self, endpoint_url: str, api_key: str, timeout: int = 15):
        """
        Initialize API Tester
        
        Args:
            endpoint_url: The participant's API endpoint
            api_key: Authorization token/API key
            timeout: Request timeout in seconds (default: 15)
        """
        self.endpoint_url = endpoint_url.strip()
        self.api_key = api_key.strip()
        self.timeout = timeout
    
    def build_payload(
        self,
        audio_mode: str = "url",
        audio_url: str = "",
        audio_base64: str = "",
        language: str = "auto",
        message: str = ""
    ) -> Dict[str, Any]:
        """
        Build the JSON payload based on audio input mode
        
        Args:
            audio_mode: "url" or "base64"
            audio_url: URL of the audio file (if mode is "url")
            audio_base64: Base64 encoded audio (if mode is "base64")
            language: Language code (auto, en, hi, ta, ml, te)
            message: Optional test message for reference
        
        Returns:
            Dictionary containing the request payload
        """
        payload = {
            "language": language,
            "metadata": {
                "message": message if message else "API Test Request",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "tester": "AI Voice API Tester v2.0"
            }
        }
        
        # Add audio based on mode - NEVER both
        if audio_mode == "url":
            payload["audio_url"] = audio_url.strip()
        else:
            payload["audio_base64"] = audio_base64.strip()
        
        return payload
    
    def build_headers(self) -> Dict[str, str]:
        """
        Build request headers with authorization
        
        Returns:
            Dictionary containing request headers
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        return headers
    
    def send_request(
        self,
        audio_mode: str = "url",
        audio_url: str = "",
        audio_base64: str = "",
        language: str = "auto",
        message: str = ""
    ) -> TestResult:
        """
        Send POST request to the API and measure results
        
        Args:
            audio_mode: "url" or "base64"
            audio_url: URL of the audio file
            audio_base64: Base64 encoded audio
            language: Language code
            message: Optional test message
        
        Returns:
            TestResult object containing all test data
        """
        payload = self.build_payload(
            audio_mode=audio_mode,
            audio_url=audio_url,
            audio_base64=audio_base64,
            language=language,
            message=message
        )
        headers = self.build_headers()
        
        start_time = time.perf_counter()
        
        try:
            response = requests.post(
                self.endpoint_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except Exception:
                response_data = None
            
            return TestResult(
                success=(200 <= response.status_code < 300),
                status_code=response.status_code,
                latency_ms=round(latency_ms, 2),
                response_data=response_data,
                error_message="",
                raw_response=response.text[:2000]  # Limit raw response size
            )
            
        except requests.exceptions.Timeout:
            return TestResult(
                success=False,
                status_code=408,
                latency_ms=self.timeout * 1000,
                response_data=None,
                error_message=f"Request timed out after {self.timeout} seconds",
                raw_response=""
            )
            
        except requests.exceptions.ConnectionError as e:
            return TestResult(
                success=False,
                status_code=0,
                latency_ms=0,
                response_data=None,
                error_message=f"Connection failed: Unable to reach the endpoint. Check if URL is correct.",
                raw_response=str(e)[:500]
            )
            
        except requests.exceptions.RequestException as e:
            return TestResult(
                success=False,
                status_code=0,
                latency_ms=0,
                response_data=None,
                error_message=f"Request failed: {str(e)}",
                raw_response=""
            )
        
        except Exception as e:
            return TestResult(
                success=False,
                status_code=0,
                latency_ms=0,
                response_data=None,
                error_message=f"Unexpected error: {str(e)}",
                raw_response=""
            )
    
    def get_result(
        self,
        audio_mode: str = "url",
        audio_url: str = "",
        audio_base64: str = "",
        language: str = "auto",
        message: str = ""
    ) -> TestResult:
        """
        Execute test and return result (alias for send_request)
        """
        return self.send_request(
            audio_mode=audio_mode,
            audio_url=audio_url,
            audio_base64=audio_base64,
            language=language,
            message=message
        )
