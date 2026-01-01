from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union
from utils.date_helper import get_current_date, parse_date_input


@dataclass
class Transaction:
    """Transaction model"""
    amount: float
    type: str  # 'income' or 'expense'
    category: str
    description: Optional[str] = None
    payment_method: Optional[str] = None
    project: Optional[str] = None
    date: Optional[Union[str, datetime]] = None  # Строка в формате ДД.ММ.ГГГГ или ГГГГ
    user_telegram_id: Optional[int] = None
    ai_categorized: bool = False
    voice_transcription: Optional[str] = None
    receipt_image_url: Optional[str] = None
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    currency: str = 'UAH'  # UAH, USD, EUR
    original_amount: Optional[float] = None
    original_currency: Optional[str] = None
    is_team_finance: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion"""
        data = {
            'amount': self.amount,
            'type': self.type,
            'category': self.category,
            'currency': self.currency,
            'is_team_finance': self.is_team_finance,
        }

        if self.description:
            data['description'] = self.description
        if self.payment_method:
            data['payment_method'] = self.payment_method
        if self.project:
            data['project'] = self.project
        if self.date:
            # Конвертируем дату в ISO формат для базы данных
            if isinstance(self.date, str):
                # Если строка в формате ДД.ММ.ГГГГ - конвертируем в timestamp
                if '.' in self.date:
                    parts = self.date.split('.')
                    if len(parts) == 3:
                        day, month, year = parts
                        data['date'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}T00:00:00Z"
                    else:
                        data['date'] = datetime.now().isoformat()
                # Если только год - используем 1 января
                elif len(self.date) == 4 and self.date.isdigit():
                    data['date'] = f"{self.date}-01-01T00:00:00Z"
                else:
                    data['date'] = self.date  # Уже в правильном формате
            else:
                # datetime объект
                data['date'] = self.date.isoformat()
        else:
            # Если дата не указана, используем текущую
            data['date'] = datetime.now().isoformat()
        if self.user_telegram_id:
            data['user_telegram_id'] = self.user_telegram_id
        if self.ai_categorized is not None:
            data['ai_categorized'] = self.ai_categorized
        if self.voice_transcription:
            data['voice_transcription'] = self.voice_transcription
        if self.receipt_image_url:
            data['receipt_image_url'] = self.receipt_image_url
        if self.original_amount:
            data['original_amount'] = self.original_amount
        if self.original_currency:
            data['original_currency'] = self.original_currency

        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Create Transaction from dictionary"""
        # Обработка даты - оставляем как строку
        date_value = data.get('date')

        return cls(
            id=data.get('id'),
            amount=float(data.get('amount', 0)),
            type=data.get('type', ''),
            category=data.get('category', ''),
            description=data.get('description'),
            payment_method=data.get('payment_method'),
            project=data.get('project'),
            date=date_value,  # Сохраняем как строку
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            user_telegram_id=data.get('user_telegram_id'),
            ai_categorized=data.get('ai_categorized', False),
            voice_transcription=data.get('voice_transcription'),
            receipt_image_url=data.get('receipt_image_url'),
            currency=data.get('currency', 'UAH'),
            original_amount=data.get('original_amount'),
            original_currency=data.get('original_currency'),
            is_team_finance=data.get('is_team_finance', False),
        )
