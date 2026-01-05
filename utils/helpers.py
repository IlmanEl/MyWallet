from datetime import datetime, timedelta
from typing import Tuple
import re


def parse_amount(text: str) -> float:
    """
    Extract amount from text
    Examples: "500", "1,200", "1200.50"
    """
    cleaned = re.sub(r'[^\d.,]', '', text)
    cleaned = cleaned.replace(',', '')

    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def format_currency(amount: float, currency: str = "грн") -> str:
    """Format amount as currency string"""
    return f"{amount:,.2f} {currency}"


def get_date_range(period: str) -> Tuple[datetime, datetime]:
    """
    Get date range for different periods
    period: 'day', 'week', 'month', 'year', 'all'
    """
    now = datetime.now()

    if period == 'day':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == 'week':
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == 'month':
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == 'year':
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == 'all':
        # За все время - начало с 2020 года
        start = datetime(2020, 1, 1)
        end = now
    else:
        raise ValueError(f"Invalid period: {period}")

    return start, end


def format_date(date: datetime, format_type: str = 'default') -> str:
    """Format datetime to string"""
    if format_type == 'default':
        return date.strftime('%d.%m.%Y')
    elif format_type == 'datetime':
        return date.strftime('%d.%m.%Y %H:%M')
    elif format_type == 'time':
        return date.strftime('%H:%M')
    else:
        return date.strftime('%d.%m.%Y')


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'


def get_currency_symbol(currency: str) -> str:
    """Get currency symbol"""
    symbols = {
        'UAH': '₴',
        'USD': '$',
        'EUR': '€'
    }
    return symbols.get(currency, currency)
