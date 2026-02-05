"""
UI Components Module - Reusable Streamlit UI Elements
Enhanced with Audio Mode Toggle & Language Selector
"""
import streamlit as st
import json
from typing import Dict, Any, List, Optional


# Supported Languages
LANGUAGES = {
    "auto": "🌐 Auto Detect",
    "en": "🇬🇧 English",
    "hi": "🇮🇳 Hindi",
    "ta": "🇮🇳 Tamil",
    "ml": "🇮🇳 Malayalam",
    "te": "🇮🇳 Telugu"
}


def render_header():
    """Render the main header with styling"""
    st.markdown("""
    <div class="main-header">
        <h1>🎤 AI Voice Detection API Tester</h1>
        <p class="subtitle">Hackathon Judge Tool - Test & Validate Participant APIs</p>
        <p class="feature-badge">✨ Multi-language supported</p>
    </div>
    """, unsafe_allow_html=True)


def render_input_section() -> Dict[str, Any]:
    """
    Render input fields with audio mode toggle and language selector
    
    Returns:
        Dictionary with endpoint_url, api_key, audio_mode, audio_url/audio_base64, language, message
    """
    st.markdown("### 📝 API Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        endpoint_url = st.text_input(
            "🔗 API Endpoint URL",
            placeholder="https://participant-api.com/detect",
            help="Enter the participant's API endpoint URL (POST)"
        )
    
    with col2:
        api_key = st.text_input(
            "🔑 API Key / Auth Token",
            type="password",
            placeholder="Enter API key or Bearer token",
            help="Authorization token - will be sent as: Bearer <token>"
        )
    
    st.markdown("---")
    st.markdown("### 🎵 Audio Input")
    
    # Audio Mode Toggle
    audio_mode = st.radio(
        "Select Audio Input Mode:",
        options=["url", "base64"],
        format_func=lambda x: "🔗 Audio via URL" if x == "url" else "📝 Audio via Base64",
        horizontal=True,
        help="Choose how to provide the audio file"
    )
    
    audio_url = ""
    audio_base64 = ""
    
    if audio_mode == "url":
        audio_url = st.text_input(
            "🎵 Audio File URL",
            placeholder="https://example.com/audio.mp3",
            help="URL of the audio file to test (.mp3 or .wav)"
        )
    else:
        audio_base64 = st.text_area(
            "📝 Audio Base64 Data",
            placeholder="Paste Base64 encoded audio here...",
            height=120,
            help="Base64 encoded audio content"
        )
        st.caption("💡 **Hint:** MP3 must be Base64-encoded, no data URI prefix (no `data:audio/mp3;base64,`)")
    
    st.markdown("---")
    st.markdown("### 🌍 Language & Message")
    
    col1, col2 = st.columns(2)
    
    with col1:
        language = st.selectbox(
            "🗣️ Language",
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            help="Select the language of the audio or Auto Detect"
        )
    
    with col2:
        message = st.text_input(
            "💬 Test Message (Optional)",
            placeholder="Test request from judges",
            help="Optional reference message for the test"
        )
    
    return {
        "endpoint_url": endpoint_url,
        "api_key": api_key,
        "audio_mode": audio_mode,
        "audio_url": audio_url,
        "audio_base64": audio_base64,
        "language": language,
        "message": message
    }


def render_result_card(verdict: str, message: str, severity: str = "success"):
    """
    Render Pass/Fail result card
    
    Args:
        verdict: PASS, FAIL, or UNKNOWN
        message: Description message
        severity: success, error, or warning
    """
    if verdict == "PASS":
        icon = "✅"
        card_class = "result-pass"
    elif verdict == "FAIL":
        icon = "❌"
        card_class = "result-fail"
    else:
        icon = "⚠️"
        card_class = "result-warning"
    
    st.markdown(f"""
    <div class="result-card {card_class}">
        <div class="result-icon">{icon}</div>
        <div class="result-content">
            <h3>{verdict}</h3>
            <p>{message}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metrics(latency_ms: float, status_code: int, response_data: Optional[Dict] = None):
    """
    Render performance metrics - Updated for new schema
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="⏱️ Latency",
            value=f"{latency_ms:.0f} ms",
            delta="Fast" if latency_ms < 1000 else ("Slow" if latency_ms > 3000 else None),
            delta_color="normal" if latency_ms < 1000 else "inverse"
        )
    
    with col2:
        st.metric(
            label="📊 Status Code",
            value=status_code if status_code > 0 else "N/A"
        )
    
    with col3:
        if response_data and "confidence" in response_data:
            conf = float(response_data["confidence"]) * 100
            st.metric(
                label="🎯 Confidence",
                value=f"{conf:.1f}%"
            )
        else:
            st.metric(label="🎯 Confidence", value="N/A")
    
    with col4:
        # Check for both 'classification' (new) and 'result' (old) for backward compatibility
        classification = response_data.get("classification") or response_data.get("result") if response_data else None
        if classification:
            st.metric(
                label="🤖 Classification",
                value=classification
            )
        else:
            st.metric(label="🤖 Classification", value="N/A")


def render_explanation(response_data: Optional[Dict] = None):
    """
    Render AI explanation from response
    """
    if response_data and "explanation" in response_data and response_data["explanation"]:
        st.markdown("### 💡 AI Explanation")
        st.info(f"🧠 {response_data['explanation']}")


def render_detected_language(response_data: Optional[Dict] = None):
    """
    Render detected language from response
    """
    if response_data and "language" in response_data:
        lang = response_data["language"]
        lang_display = LANGUAGES.get(lang, f"🌐 {lang}")
        st.markdown(f"**🗣️ Detected Language:** {lang_display}")


def render_json_viewer(data: Dict[str, Any], title: str = "Response Data"):
    """
    Render formatted JSON with syntax highlighting
    """
    with st.expander(f"📋 {title}", expanded=True):
        st.json(data)


def render_raw_response(raw: str, title: str = "Raw Response"):
    """
    Render raw response text
    """
    if raw:
        with st.expander(f"📄 {title}", expanded=False):
            st.code(raw, language="text")


def render_schema_warnings(warnings: List[str]):
    """
    Render schema validation warnings
    """
    if warnings:
        st.markdown("### ⚠️ Schema Warnings")
        for warning in warnings:
            st.warning(warning)


def render_error(error_message: str):
    """
    Render error message
    """
    st.error(f"🚨 **Error:** {error_message}")


def render_test_button() -> bool:
    """
    Render the test execution button
    
    Returns:
        True if button was clicked
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        return st.button(
            "🚀 Run API Test",
            type="primary",
            use_container_width=True
        )


def render_validation_errors(errors: List[str]):
    """
    Render input validation errors
    """
    for error in errors:
        st.error(f"⛔ {error}")


def render_footer():
    """Render footer"""
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p>🏆 AI Voice Detection API Tester | Built for Hackathon Judges</p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem;">Supports: English • Hindi • Tamil • Malayalam • Telugu</p>
    </div>
    """, unsafe_allow_html=True)
