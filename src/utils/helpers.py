"""
Helper utility functions
"""
from typing import Optional, Union
from datetime import datetime


def format_price(price: float, currency: str = "USD") -> str:
    """Format price with appropriate decimal places"""
    if price >= 1:
        return f"${price:,.2f}"
    elif price >= 0.01:
        return f"${price:,.4f}"
    else:
        return f"${price:.8f}"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100


def validate_symbol(symbol: str) -> bool:
    """Validate cryptocurrency symbol format"""
    if not symbol or not isinstance(symbol, str):
        return False
    
    # Basic validation: 2-10 characters, alphanumeric
    symbol = symbol.strip().upper()
    return 2 <= len(symbol) <= 10 and symbol.isalnum()


def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for display"""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")


def safe_float(value: Union[str, float, int, None]) -> Optional[float]:
    """Safely convert value to float"""
    if value is None:
        return None
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def truncate_string(text: str, max_length: int = 100) -> str:
    """Truncate string to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
