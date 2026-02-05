"""
Validators Module - Request/Response Validation
Enhanced with new schema: classification, explanation, language validation
"""
import re
import base64
from urllib.parse import urlparse
from typing import Dict, Any, Tuple, List


# Valid Languages
VALID_LANGUAGES = ["auto", "en", "hi", "ta", "ml", "te"]


# Expected Response Schema (Updated)
EXPECTED_SCHEMA = {
    "required_fields": ["status", "classification", "confidence", "explanation"],
    "optional_fields": ["language", "processing_time_ms"],
    "valid_status": ["success", "error"],
    "valid_classifications": ["AI_GENERATED", "HUMAN", "UNKNOWN"]
}


def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate if URL format is correct
    Returns: (is_valid, error_message)
    """
    if not url or not url.strip():
        return False, "URL cannot be empty"
    
    try:
        parsed = urlparse(url.strip())
        if parsed.scheme not in ['http', 'https']:
            return False, "URL must start with http:// or https://"
        if not parsed.netloc:
            return False, "Invalid URL format - missing domain"
        return True, ""
    except Exception as e:
        return False, f"URL parsing error: {str(e)}"


def validate_audio_url(url: str) -> Tuple[bool, str]:
    """
    Validate if audio URL has valid format (.mp3 or .wav)
    Returns: (is_valid, error_message)
    """
    is_valid_url, error = validate_url(url)
    if not is_valid_url:
        return False, error
    
    # Check for valid audio extensions
    lower_url = url.lower().split('?')[0]  # Remove query params
    if not (lower_url.endswith('.mp3') or lower_url.endswith('.wav')):
        return False, "Audio URL must end with .mp3 or .wav"
    
    return True, ""


def validate_audio_base64(base64_string: str) -> Tuple[bool, str]:
    """
    Validate if Base64 string is valid
    Returns: (is_valid, error_message)
    """
    if not base64_string or not base64_string.strip():
        return False, "Base64 audio data cannot be empty"
    
    # Remove any potential data URI prefix
    cleaned = base64_string.strip()
    if cleaned.startswith('data:'):
        return False, "Remove data URI prefix (e.g., 'data:audio/mp3;base64,'). Provide only the Base64 content."
    
    # Check if it's valid Base64
    try:
        # Try to decode to verify it's valid Base64
        decoded = base64.b64decode(cleaned, validate=True)
        if len(decoded) < 100:
            return False, "Base64 data seems too short for an audio file"
        return True, ""
    except Exception as e:
        return False, f"Invalid Base64 encoding: {str(e)}"


def validate_api_key(api_key: str) -> Tuple[bool, str]:
    """
    Validate API key is not empty
    Returns: (is_valid, error_message)
    """
    if not api_key or not api_key.strip():
        return False, "API Key cannot be empty"
    return True, ""


def validate_language(language: str) -> Tuple[bool, str]:
    """
    Validate if language is in the allowed list
    Returns: (is_valid, error_message)
    """
    if language not in VALID_LANGUAGES:
        return False, f"Invalid language '{language}'. Allowed: {VALID_LANGUAGES}"
    return True, ""


def validate_response_schema(response: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate if response matches expected schema (Updated)
    Returns: (is_valid, list_of_warnings)
    """
    warnings = []
    is_valid = True
    
    # Check required fields
    for field in EXPECTED_SCHEMA["required_fields"]:
        if field not in response:
            warnings.append(f"Missing required field: '{field}'")
            is_valid = False
    
    # Validate 'status' field
    if "status" in response:
        if response["status"] not in EXPECTED_SCHEMA["valid_status"]:
            warnings.append(f"Invalid status value: '{response['status']}'. Expected: {EXPECTED_SCHEMA['valid_status']}")
    
    # Validate 'classification' field (new - replaces 'result')
    if "classification" in response:
        if response["classification"] not in EXPECTED_SCHEMA["valid_classifications"]:
            warnings.append(f"Invalid classification value: '{response['classification']}'. Expected: {EXPECTED_SCHEMA['valid_classifications']}")
    
    # Backward compatibility: check for old 'result' field
    if "result" in response and "classification" not in response:
        warnings.append("Using deprecated 'result' field. Should use 'classification' instead.")
    
    # Validate 'confidence' field
    if "confidence" in response:
        try:
            conf = float(response["confidence"])
            if conf < 0 or conf > 1:
                warnings.append(f"Confidence should be between 0 and 1, got: {conf}")
        except (ValueError, TypeError):
            warnings.append(f"Confidence should be a number, got: {type(response['confidence']).__name__}")
    
    # Validate 'explanation' field
    if "explanation" in response:
        if not response["explanation"] or not str(response["explanation"]).strip():
            warnings.append("Explanation field is empty. Should provide reasoning for the classification.")
    
    # Validate 'language' field if present
    if "language" in response:
        if response["language"] not in VALID_LANGUAGES:
            warnings.append(f"Invalid language value: '{response['language']}'. Expected: {VALID_LANGUAGES}")
    
    # Check for extra unexpected fields
    all_expected = set(EXPECTED_SCHEMA["required_fields"] + EXPECTED_SCHEMA["optional_fields"])
    # Also allow deprecated 'result' field for backward compatibility
    all_expected.add("result")
    extra_fields = set(response.keys()) - all_expected
    if extra_fields:
        warnings.append(f"Extra fields in response: {list(extra_fields)}")
    
    return is_valid, warnings


def interpret_status_code(status_code: int) -> Dict[str, Any]:
    """
    Interpret HTTP status code and return verdict
    """
    status_map = {
        200: {"verdict": "PASS", "message": "Success - API responded correctly", "severity": "success"},
        201: {"verdict": "PASS", "message": "Created - Request processed", "severity": "success"},
        400: {"verdict": "FAIL", "message": "Bad Request - Check your payload format", "severity": "error"},
        401: {"verdict": "FAIL", "message": "Unauthorized - Invalid or missing API key", "severity": "error"},
        403: {"verdict": "FAIL", "message": "Forbidden - API key lacks permissions", "severity": "error"},
        404: {"verdict": "FAIL", "message": "Not Found - Wrong endpoint URL", "severity": "error"},
        405: {"verdict": "FAIL", "message": "Method Not Allowed - Endpoint doesn't accept POST", "severity": "error"},
        408: {"verdict": "FAIL", "message": "Request Timeout - API took too long", "severity": "warning"},
        422: {"verdict": "FAIL", "message": "Unprocessable Entity - Invalid data format", "severity": "error"},
        429: {"verdict": "FAIL", "message": "Too Many Requests - Rate limit exceeded", "severity": "warning"},
        500: {"verdict": "FAIL", "message": "Internal Server Error - API crashed", "severity": "error"},
        502: {"verdict": "FAIL", "message": "Bad Gateway - Server unreachable", "severity": "error"},
        503: {"verdict": "FAIL", "message": "Service Unavailable - API is down", "severity": "error"},
        504: {"verdict": "FAIL", "message": "Gateway Timeout - Server didn't respond", "severity": "error"},
    }
    
    if status_code in status_map:
        return status_map[status_code]
    elif 200 <= status_code < 300:
        return {"verdict": "PASS", "message": f"Success ({status_code})", "severity": "success"}
    elif 400 <= status_code < 500:
        return {"verdict": "FAIL", "message": f"Client Error ({status_code})", "severity": "error"}
    elif status_code >= 500:
        return {"verdict": "FAIL", "message": f"Server Error ({status_code})", "severity": "error"}
    else:
        return {"verdict": "UNKNOWN", "message": f"Unexpected status code: {status_code}", "severity": "warning"}
