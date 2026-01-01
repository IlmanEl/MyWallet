"""
Date Helper
Утилита для работы с датами в формате ДД.ММ.ГГГГ или только ГГГГ
"""

from datetime import datetime
from typing import Optional


def parse_date_input(date_str: Optional[str] = None) -> str:
    """
    Парсит ввод даты пользователя

    Форматы:
    - None или "сегодня" -> текущая дата в формате ДД.ММ.ГГГГ
    - "2025" -> только год
    - "25.11.2024" -> полная дата ДД.ММ.ГГГГ
    - "25.11" -> добавляет текущий год

    Returns:
        str: Дата в формате ДД.ММ.ГГГГ или ГГГГ
    """
    if not date_str or date_str.lower() in ['сегодня', 'today']:
        # Текущая дата в формате ДД.ММ.ГГГГ
        now = datetime.now()
        return now.strftime('%d.%m.%Y')

    date_str = date_str.strip()

    # Только год (например, "2025")
    if len(date_str) == 4 and date_str.isdigit():
        return date_str

    # Формат ДД.ММ.ГГГГ
    parts = date_str.split('.')

    if len(parts) == 3:
        # Полная дата
        day, month, year = parts
        return f"{day.zfill(2)}.{month.zfill(2)}.{year}"

    elif len(parts) == 2:
        # ДД.ММ - добавляем текущий год
        day, month = parts
        year = datetime.now().year
        return f"{day.zfill(2)}.{month.zfill(2)}.{year}"

    # Если не удалось распарсить, возвращаем текущую дату
    now = datetime.now()
    return now.strftime('%d.%m.%Y')


def get_current_date() -> str:
    """
    Возвращает текущую дату в формате ДД.ММ.ГГГГ
    """
    return datetime.now().strftime('%d.%m.%Y')


def format_date_for_display(date_str: str) -> str:
    """
    Форматирует дату для отображения пользователю

    Args:
        date_str: Дата в любом формате (ГГГГ или ДД.ММ.ГГГГ)

    Returns:
        str: Отформатированная дата
    """
    if not date_str:
        return "Не указано"

    # Если только год
    if len(date_str) == 4 and date_str.isdigit():
        return f"{date_str} год"

    # Если полная дата ДД.ММ.ГГГГ
    if '.' in date_str:
        return date_str

    # Попытка парсить ISO формат (из базы)
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%d.%m.%Y')
    except:
        return date_str


def is_year_only(date_str: str) -> bool:
    """
    Проверяет, указан ли только год
    """
    return len(date_str) == 4 and date_str.isdigit()
