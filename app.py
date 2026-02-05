"""
🎤 AI Voice Detection API Tester
Hackathon Judge Tool - Test & Validate Participant APIs
Enhanced with Audio Mode Toggle, Language Selection, and Schema Validation
"""
import streamlit as st
import json
import os

# Import custom components
from components.api_tester import APITester
from components.validators import (
    validate_url,
    validate_audio_url,
    validate_audio_base64,
    validate_api_key,
    validate_language,
    validate_response_schema,
    interpret_status_code,
    VALID_LANGUAGES
)
from components.ui_components import (
    render_header,
    render_input_section,
    render_result_card,
    render_metrics,
    render_explanation,
    render_detected_language,
    render_json_viewer,
    render_raw_response,
    render_schema_warnings,
    render_error,
    render_test_button,
    render_validation_errors,
    render_footer,
    LANGUAGES
)

# Page configuration
st.set_page_config(
    page_title="AI Voice API Tester",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Additional inline styles for immediate effect
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    }
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .main-header h1 {
        font-size: 2.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .main-header .subtitle {
        color: #a0a0a0;
        font-size: 1.1rem;
    }
    .main-header .feature-badge {
        color: #00ff88;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    .result-card {
        display: flex;
        align-items: center;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    .result-pass {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.15) 0%, rgba(0, 200, 100, 0.1) 100%);
        border: 1px solid rgba(0, 255, 136, 0.3);
    }
    .result-fail {
        background: linear-gradient(135deg, rgba(255, 0, 68, 0.15) 0%, rgba(200, 0, 50, 0.1) 100%);
        border: 1px solid rgba(255, 0, 68, 0.3);
    }
    .result-warning {
        background: linear-gradient(135deg, rgba(255, 170, 0, 0.15) 0%, rgba(200, 130, 0, 0.1) 100%);
        border: 1px solid rgba(255, 170, 0, 0.3);
    }
    .result-icon {
        font-size: 3rem;
        margin-right: 1.5rem;
    }
    .result-content h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1.5rem;
        color: #ffffff;
    }
    .result-content p {
        margin: 0;
        color: #cccccc;
    }
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #666666;
    }
</style>
""", unsafe_allow_html=True)

# Render header
render_header()

# Sidebar for settings
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    timeout = st.slider(
        "Request Timeout (seconds)",
        min_value=5,
        max_value=30,
        value=15,
        help="Maximum time to wait for API response"
    )
    
    st.markdown("---")
    st.markdown("### 📖 Expected Response Schema")
    st.code("""
{
  "status": "success",
  "classification": "AI_GENERATED",
  "confidence": 0.87,
  "language": "en",
  "explanation": "Spectral...",
  "processing_time_ms": 842
}
    """, language="json")
    
    st.markdown("---")
    st.markdown("### 🗣️ Supported Languages")
    for code, name in LANGUAGES.items():
        st.markdown(f"- `{code}` → {name}")
    
    st.markdown("---")
    st.markdown("### ℹ️ Status Codes")
    st.markdown("""
    - **200** ✅ Success
    - **401** 🔒 Unauthorized
    - **403** 🚫 Forbidden
    - **404** ❓ Not Found
    - **405** ⛔ Method Not Allowed
    - **500** 💥 Server Error
    """)

# Main content
st.markdown("---")

# Input section
inputs = render_input_section()

st.markdown("---")

# Validation before test
def validate_inputs(inputs):
    """Validate all inputs and return list of errors"""
    errors = []
    
    # Validate endpoint URL
    is_valid, error = validate_url(inputs["endpoint_url"])
    if not is_valid:
        errors.append(f"Endpoint URL: {error}")
    
    # Validate API key
    is_valid, error = validate_api_key(inputs["api_key"])
    if not is_valid:
        errors.append(f"API Key: {error}")
    
    # Validate audio based on mode
    if inputs["audio_mode"] == "url":
        is_valid, error = validate_audio_url(inputs["audio_url"])
        if not is_valid:
            errors.append(f"Audio URL: {error}")
    else:
        is_valid, error = validate_audio_base64(inputs["audio_base64"])
        if not is_valid:
            errors.append(f"Audio Base64: {error}")
    
    # Validate language
    is_valid, error = validate_language(inputs["language"])
    if not is_valid:
        errors.append(f"Language: {error}")
    
    return errors

# Test button
if render_test_button():
    # Validate inputs first
    validation_errors = validate_inputs(inputs)
    
    if validation_errors:
        st.markdown("### ⚠️ Validation Errors")
        render_validation_errors(validation_errors)
    else:
        # Run the test
        with st.spinner("🔄 Testing API... Please wait..."):
            # Create tester instance
            tester = APITester(
                endpoint_url=inputs["endpoint_url"],
                api_key=inputs["api_key"],
                timeout=timeout
            )
            
            # Execute test with new parameters
            result = tester.get_result(
                audio_mode=inputs["audio_mode"],
                audio_url=inputs["audio_url"],
                audio_base64=inputs["audio_base64"],
                language=inputs["language"],
                message=inputs["message"]
            )
        
        # Display results
        st.markdown("---")
        st.markdown("## 📊 Test Results")
        
        # Interpret status code
        status_info = interpret_status_code(result.status_code)
        
        # Show main verdict
        render_result_card(
            verdict=status_info["verdict"],
            message=status_info["message"],
            severity=status_info["severity"]
        )
        
        # Show metrics
        st.markdown("### 📈 Performance Metrics")
        render_metrics(
            latency_ms=result.latency_ms,
            status_code=result.status_code,
            response_data=result.response_data
        )
        
        # Show explanation if available
        if result.response_data:
            render_explanation(result.response_data)
            render_detected_language(result.response_data)
        
        # Show error if any
        if result.error_message:
            st.markdown("### 🚨 Error Details")
            render_error(result.error_message)
        
        # Response data section
        if result.response_data:
            # Validate response schema
            is_valid_schema, schema_warnings = validate_response_schema(result.response_data)
            
            if schema_warnings:
                render_schema_warnings(schema_warnings)
            else:
                st.success("✅ Response schema is valid!")
            
            # Show response data
            render_json_viewer(result.response_data, "API Response")
        
        # Show raw response if no parsed data
        if result.raw_response and not result.response_data:
            render_raw_response(result.raw_response)
        
        # Request details (collapsible)
        with st.expander("📤 Request Details", expanded=False):
            st.markdown("**Endpoint:**")
            st.code(inputs["endpoint_url"])
            
            st.markdown("**Headers:**")
            st.json({
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer [HIDDEN]"
            })
            
            st.markdown("**Payload:**")
            payload = tester.build_payload(
                audio_mode=inputs["audio_mode"],
                audio_url=inputs["audio_url"],
                audio_base64=inputs["audio_base64"][:50] + "..." if len(inputs["audio_base64"]) > 50 else inputs["audio_base64"],
                language=inputs["language"],
                message=inputs["message"]
            )
            st.json(payload)

# Sample test section
st.markdown("---")
with st.expander("🧪 Quick Test with Sample Data", expanded=False):
    st.markdown("""
    **Want to test the UI quickly?** Use these sample values:
    
    #### URL Mode:
    - **Endpoint URL:** `https://httpbin.org/post` (echo server for testing)
    - **API Key:** `test-api-key-12345`
    - **Audio URL:** `https://example.com/sample.mp3`
    - **Language:** Auto Detect
    
    #### Base64 Mode:
    - Use a small Base64-encoded MP3/WAV file
    - No data URI prefix (no `data:audio/mp3;base64,`)
    
    *Note: httpbin.org will echo back your request, not perform actual AI detection.*
    """)

# Footer
render_footer()
