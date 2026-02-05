"""
Utility Helper Functions
"""
import time
from datetime import datetime


def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def format_latency(ms: float) -> str:
    """Format latency with appropriate unit"""
    if ms < 1000:
        return f"{ms:.0f} ms"
    else:
        return f"{ms/1000:.2f} s"


def get_latency_color(ms: float) -> str:
    """Get color based on latency value"""
    if ms < 500:
        return "#00ff88"  # Green - excellent
    elif ms < 1000:
        return "#88ff00"  # Light green - good
    elif ms < 2000:
        return "#ffaa00"  # Orange - acceptable
    elif ms < 3000:
        return "#ff6600"  # Dark orange - slow
    else:
        return "#ff0044"  # Red - too slow


def truncate_string(s: str, max_length: int = 100) -> str:
    """Truncate string with ellipsis"""
    if len(s) <= max_length:
        return s
    return s[:max_length-3] + "..."
