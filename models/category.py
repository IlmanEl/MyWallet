from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    """Category model"""
    name: str
    type: str  # 'income' or 'expense'
    emoji: Optional[str] = None
    parent_category: Optional[str] = None
    id: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion"""
        data = {
            'name': self.name,
            'type': self.type,
        }

        if self.emoji:
            data['emoji'] = self.emoji
        if self.parent_category:
            data['parent_category'] = self.parent_category

        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Category':
        """Create Category from dictionary"""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            type=data.get('type', ''),
            emoji=data.get('emoji'),
            parent_category=data.get('parent_category'),
        )

    def display_name(self) -> str:
        """Get display name with emoji"""
        if self.emoji:
            return f"{self.emoji} {self.name}"
        return self.name
