from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Transaction:
    """Transaction model"""
    amount: float
    type: str  # 'income' or 'expense'
    category: str
    description: Optional[str] = None
    payment_method: Optional[str] = None
    project: Optional[str] = None
    date: Optional[datetime] = None
    user_telegram_id: Optional[int] = None
    ai_categorized: bool = False
    voice_transcription: Optional[str] = None
    receipt_image_url: Optional[str] = None
    id: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion"""
        data = {
            'amount': self.amount,
            'type': self.type,
            'category': self.category,
        }

        if self.description:
            data['description'] = self.description
        if self.payment_method:
            data['payment_method'] = self.payment_method
        if self.project:
            data['project'] = self.project
        if self.date:
            data['date'] = self.date.isoformat()
        if self.user_telegram_id:
            data['user_telegram_id'] = self.user_telegram_id
        if self.ai_categorized is not None:
            data['ai_categorized'] = self.ai_categorized
        if self.voice_transcription:
            data['voice_transcription'] = self.voice_transcription
        if self.receipt_image_url:
            data['receipt_image_url'] = self.receipt_image_url

        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Create Transaction from dictionary"""
        return cls(
            id=data.get('id'),
            amount=float(data.get('amount', 0)),
            type=data.get('type', ''),
            category=data.get('category', ''),
            description=data.get('description'),
            payment_method=data.get('payment_method'),
            project=data.get('project'),
            date=datetime.fromisoformat(data['date']) if data.get('date') else None,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            user_telegram_id=data.get('user_telegram_id'),
            ai_categorized=data.get('ai_categorized', False),
            voice_transcription=data.get('voice_transcription'),
            receipt_image_url=data.get('receipt_image_url'),
        )
