from services.ai_service import ai_service
from services.database import db
import logging

logger = logging.getLogger(__name__)


class CategorizationService:
    """Service for smart categorization of transactions"""

    @staticmethod
    def get_available_categories(transaction_type: str) -> list:
        """Get list of available categories for a transaction type"""
        categories = db.get_categories(category_type=transaction_type)
        return [cat['name'] for cat in categories if not cat.get('parent_category')]

    @staticmethod
    def auto_categorize(description: str, amount: float, transaction_type: str) -> str:
        """Automatically categorize a transaction"""
        try:
            available_categories = CategorizationService.get_available_categories(transaction_type)

            if not available_categories:
                return "Другое"

            category = ai_service.categorize_transaction(
                description=description,
                amount=amount,
                transaction_type=transaction_type,
                available_categories=available_categories
            )

            # Validate that returned category exists
            if category in available_categories:
                return category
            else:
                logger.warning(f"AI returned invalid category: {category}")
                return "Другое"

        except Exception as e:
            logger.error(f"Error in auto categorization: {e}")
            return "Другое"

    @staticmethod
    def suggest_subcategory(parent_category: str, transaction_type: str) -> list:
        """Get subcategories for a parent category"""
        all_categories = db.get_categories(category_type=transaction_type)
        subcategories = [
            cat for cat in all_categories
            if cat.get('parent_category') == parent_category
        ]
        return subcategories


categorization_service = CategorizationService()
